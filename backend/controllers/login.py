import os
import random
import string
import urllib.parse as urlparse

import requests
from flask import Blueprint, request, redirect, session

from spotify_auth import basic_auth_header, store_token_response

login_controller = Blueprint('login', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
scopes = os.getenv("SPOTIFY_SCOPES").split()
SPOTIFY_SCOPES = " ".join(scopes)


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# Sends the user to Spotify's own login/consent page. This is a full browser
# navigation (not a fetch call) since Spotify needs to show its own UI.
@login_controller.route('/api/login', methods=['GET'])
def login():
    state = generate_random_string(16)
    session['state'] = state
    auth_url = 'https://accounts.spotify.com/authorize?' + urlparse.urlencode({
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
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

    if error:
        return redirect(f"{FRONTEND_ORIGIN}/?login_error={error}")

    if state is None or state != session.get('state'):
        return redirect(f"{FRONTEND_ORIGIN}/?login_error=state_mismatch")

    data = {
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    headers = {
        'Authorization': basic_auth_header(),
        'Content-Type': "application/x-www-form-urlencoded"
    }

    r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    if r.status_code != 200:
        return redirect(f"{FRONTEND_ORIGIN}/?login_error=token_exchange_failed")

    store_token_response(r.json())
    return redirect(f"{FRONTEND_ORIGIN}/dashboard")
