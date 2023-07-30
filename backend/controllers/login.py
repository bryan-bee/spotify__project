from flask import Blueprint, request, redirect, url_for, session
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

#login function that sends the user to the spotify login page
@login_controller.route('/api/login', methods=['GET'])
def login():	
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url() + '?show_dialog=true'
    # Redirect the user to the Spotify authorization URL
    return redirect(auth_url)

#the redirect function that once the user logs in 
# and grants permission, will get send back to here
@login_controller.route('/api/redirect', methods=['GET'])
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, check_cache=False)
    session["token_info"] = token_info
    return redirect(url_for("homepage.homepage"))  # Redirect to the dashboard page or any other page

def create_spotify_oauth():
    return SpotifyOAuth(
		client_id = SPOTIFY_CLIENT_ID,
		client_secret = SPOTIFY_CLIENT_SECRET,
		redirect_uri= url_for("login.redirectPage", _external=True),
		scope = SPOTIFY_SCOPES,
        )

# if os.path.exists(r'C:\Users\Bryan\Documents\Spotipy project\backend\.cache'):
#         os.remove(r'C:\Users\Bryan\Documents\Spotipy project\backend\.cache')