import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os

homepage_controller = Blueprint('homepage', __name__)

# Spotify API base URL
#SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1/'

@homepage_controller.route('/api/homepage', methods=['GET'])
def homepage():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect(url_for("login.login"))
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # Fetch user's information
    user_info = sp.current_user()

    # Fetch user's top tracks (most listened to tracks)
    time_range = 'medium_term'  # Can be 'short_term', 'medium_term', or 'long_term'
    top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=5)

    # Process the user information and most listened tracks
    user_data = {
        'display_name': user_info.get('display_name'),
        'followers': user_info.get('followers').get('total'),
        'top_tracks': []
    }

    for track in top_tracks['items']:
        song_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        user_data['top_tracks'].append({'song_name': song_name, 'artists': artists})

    return user_data['top_tracks']

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=url_for('login.redirectPage', _external=True),
            scope="user-library-read")

