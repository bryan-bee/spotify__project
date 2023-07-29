from flask import Blueprint, request, redirect, url_for, session, jsonify
import spotipy
from flask_cors import CORS, cross_origin
from spotipy.oauth2 import SpotifyOAuth
import requests
import os
from urllib.parse import quote

login_controller = Blueprint('login', __name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET= os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI= os.getenv("SPOTIFY_REDIRECT_URI")
scopes = os.getenv("SPOTIFY_SCOPES").split()
SPOTIFY_SCOPES = " ".join(scopes)

def create_spotify_oauth():
    return SpotifyOAuth(
		client_id = SPOTIFY_CLIENT_ID,
		client_secret = SPOTIFY_CLIENT_SECRET,
		redirect_uri= url_for("login.redirectPage", _external=True),
		scope = SPOTIFY_SCOPES)

#login function that sends the user to the spotify login page
@login_controller.route('/api/login', methods=['GET'])
def login():	
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    # Redirect the user to the Spotify authorization URL
    auth_url_with_redirect = f"{auth_url}&redirect_uri={quote(sp_oauth.redirect_uri)}"
    return redirect(auth_url)

	#return jsonify({'login_url': auth_url_with_redirect})

#the redirect function that once the user logs in 
# and grants permission, will get send back to here
@login_controller.route('/api/redirect', methods=['GET'])
def redirectPage():
    #the code is what we need
    authorization_code = request.args.get('code')

    # Exchange the authorization code for an access token
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': url_for("login.redirectPage", _external=True),
        'client_id': os.getenv("SPOTIFY_CLIENT_ID"),
        'client_secret': os.getenv("SPOTIFY_CLIENT_SECRET")
    })

    if response.status_code == 200:
        access_token = response.json()['access_token']
        session['access_token'] = access_token  # Store the access token in the session
        return redirect(url_for("homepage.homepage"))  # Redirect to the dashboard page or any other page

    # Handle error if access token retrieval failed
    return 'Access token retrieval failed.', 400
