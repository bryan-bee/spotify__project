import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os
from datetime import datetime, timezone

homepage_controller = Blueprint('homepage', __name__)

@homepage_controller.route('/api/homepage', methods=['GET'])
def homepage():  
    if 'access_token' not in session or session['access_token'] == None:
        return redirect(url_for('login.login'))
    token = session['access_token']
    headers = {
        'Authorization' : 'Bearer ' + token
    }
    
    response = requests.get('https://api.spotify.com/v1/me', headers = headers)

    if response.status_code == 200:
        user_info = response.json()
    else:
        error_data = response.json()

    return user_info