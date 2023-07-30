import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os

homepage_controller = Blueprint('homepage', __name__)

@homepage_controller.route('/api/homepage', methods=['GET'])
def homepage():
    token = session['access_token']
    headers = {
        'Authorization' : 'Bearer ' + token
    }
    params ={
        'time_range' : 'long_term',
        'limit' : '5'
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

    return str(user_data['top_tracks'][0]) + str(session)