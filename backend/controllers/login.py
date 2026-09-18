import os
import random
import string
import urllib.parse as urlparse

import requests
from flask import Blueprint, request, redirect, session

from spotify_auth import basic_auth_header, store_token_response

login_controller = Blueprint('login', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
scopes = os.getenv("SPOTIFY_SCOPES").split()
SPOTIFY_SCOPES = " ".join(scopes)
IS_PRODUCTION = os.getenv("APP_ENV") == "production"


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def _redirect_uri():
    """Built from whatever host the browser actually used to reach this
    backend (127.0.0.1 for local desktop testing, a LAN IP for a phone on
    the same network, etc.) instead of a single fixed value - so switching
    which device you're testing from doesn't require editing .env every
    time. Spotify still requires each one to be pre-registered in the
    Dashboard's Redirect URIs list; this only removes the need to keep
    swapping which one is "active" in our own config."""
    return f"{request.scheme}://{request.host}/api/redirect"


def _frontend_origin():
    # In production, this same Flask app also serves the built frontend
    # (app.py's catch-all route) - genuinely the same origin, so a relative
    # path is correct and simpler than constructing one. Locally, the React
    # dev server runs separately on port 3000 of the same host Flask (port
    # 5000) was reached on, by this project's own convention, so that needs
    # a real cross-port absolute URL instead.
    if IS_PRODUCTION:
        return ""
    host = request.host.split(':')[0]
    return f"{request.scheme}://{host}:3000"


# Sends the user to Spotify's own login/consent page. This is a full browser
# navigation (not a fetch call) since Spotify needs to show its own UI.
@login_controller.route('/api/login', methods=['GET'])
def login():
    state = generate_random_string(16)
    session['state'] = state
    # The token exchange in /api/redirect must send this exact same
    # redirect_uri value back to Spotify, so it's stashed in the session now
    # rather than re-derived later (by then, the "incoming" request is
    # Spotify's own redirect, not the original browser request).
    session['oauth_redirect_uri'] = _redirect_uri()
    auth_url = 'https://accounts.spotify.com/authorize?' + urlparse.urlencode({
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': session['oauth_redirect_uri'],
        'state': state,
        'scope': SPOTIFY_SCOPES,
        'show_dialog': 'true'
    })
    return redirect(auth_url)


# Spotify redirects the browser back here after the user grants (or denies) access.
@login_controller.route('/api/redirect', methods=['GET'])
def redirectPage():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    frontend_origin = _frontend_origin()

    if error:
        return redirect(f"{frontend_origin}/?login_error={error}")

    if state is None or state != session.get('state'):
        return redirect(f"{frontend_origin}/?login_error=state_mismatch")

    data = {
        'code': code,
        'redirect_uri': session.get('oauth_redirect_uri'),
        'grant_type': 'authorization_code'
    }
    headers = {
        'Authorization': basic_auth_header(),
        'Content-Type': "application/x-www-form-urlencoded"
    }

    r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    if r.status_code != 200:
        return redirect(f"{frontend_origin}/?login_error=token_exchange_failed")

    store_token_response(r.json())
    return redirect(f"{frontend_origin}/dashboard")
