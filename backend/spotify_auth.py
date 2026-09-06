import base64
import os
from datetime import datetime, timedelta, timezone

import requests
from flask import session

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


class NotAuthenticated(Exception):
    """Raised when there is no usable Spotify session for the current user."""


def basic_auth_header():
    raw = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("utf-8")


def store_token_response(token):
    """Persist a Spotify token response (from the code exchange or a refresh) in the session."""
    session["access_token"] = token["access_token"]
    # Spotify only returns a new refresh_token sometimes; keep the old one if absent.
    if "refresh_token" in token:
        session["refresh_token"] = token["refresh_token"]
    session["expires_at"] = (
        datetime.now(timezone.utc) + timedelta(seconds=token["expires_in"])
    ).isoformat()
    session.permanent = True


def refresh_access_token():
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        raise NotAuthenticated("No refresh token in session")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Authorization": basic_auth_header(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    if response.status_code != 200:
        raise NotAuthenticated(f"Spotify refresh failed: {response.status_code} {response.text}")

    store_token_response(response.json())
    return session["access_token"]


def get_valid_access_token():
    """Return a valid access token, refreshing it first if it has expired.

    Raises NotAuthenticated if the user never logged in or the refresh token is dead
    (e.g. the user revoked access on Spotify's side).
    """
    if "access_token" not in session or "expires_at" not in session:
        raise NotAuthenticated("No Spotify session")

    expires_at = datetime.fromisoformat(session["expires_at"])
    # Refresh a little early so a request doesn't race the actual expiry.
    if datetime.now(timezone.utc) >= expires_at - timedelta(seconds=30):
        return refresh_access_token()

    return session["access_token"]
