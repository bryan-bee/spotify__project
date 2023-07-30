import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os

topTracks_controller = Blueprint('topTracks', __name__)

@topTracks_controller.route('/api/topTracks', methods=['GET', 'POST'])
def topTracks():  
    if 'access_token' not in session or session['access_token'] == None:
        return redirect(url_for('login.login'))
    token = session['access_token']
    headers = {
        'Authorization' : 'Bearer ' + token
    }
    params ={
        'time_range' : 'long_term',
        'limit' : '10'
    }
    response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers = headers, params=params)

    if response.status_code == 200:
        top_tracks = response.json()
    else:
        error_data = response.json()

    user_data = {
        'top_tracks': []
    }

    for track in top_tracks['items']:
        song_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        user_data['top_tracks'].append({'song_name': song_name, 'artists': artists})

    return user_data