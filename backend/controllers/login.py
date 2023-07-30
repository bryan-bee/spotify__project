from flask import Blueprint, request, redirect, url_for, session
from flask_cors import CORS, cross_origin
from spotipy.oauth2 import SpotifyOAuth
import requests
import os
from urllib.parse import quote
import random
import string
import urllib.parse as urlparse
from datetime import datetime, timedelta, timezone

login_controller = Blueprint('login', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET= os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI= os.getenv("SPOTIFY_REDIRECT_URI")
scopes = os.getenv("SPOTIFY_SCOPES").split()
SPOTIFY_SCOPES = " ".join(scopes)

def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

#login function that sends the user to the spotify login page
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
        'show_dialog' : 'true'
    })
    # Redirect the user to the Spotify authorization URL
    return redirect(auth_url)

#the redirect function that once the user logs in 
# and grants permission, will get send back to here
@login_controller.route('/api/redirect', methods=['GET'])
def redirectPage():
    code = request.args.get('code')
    state = request.args.get('state')

    if state is None:
        raise Exception("error with the state")
    
    data = {
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'grant_type': 'authorization_code'
        }
    
    headers = {
        'Authorization': 'Basic ' + 'NzU5OThhYjVkYmU4NDU1NDkzODUyODdlNjdkNTRlYjg6M2QxMjYxNTg1ZTEyNGNkMzhjY2NlMmE0NzY1OTI1ZmI=',
        'Content-Type' : "application/x-www-form-urlencoded"
        }
    
    r = requests.post('https://accounts.spotify.com/api/token', data= data, headers=headers)
    token = r.json()
    session['token_info'] = token
    session['access_token'] = token['access_token']
    session['expires_at'] = datetime.now(timezone.utc) + timedelta(hours=1)
    print(session)
    return redirect(url_for('homepage.homepage', _external=True))
        