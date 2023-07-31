import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os

topStuff_controller = Blueprint('topStuff', __name__)

@topStuff_controller.route('/api/topStuff', methods=['GET', 'POST'])
def topStuff():
    if 'access_token' not in session or session['access_token'] == None:
        return redirect(url_for('login.login'))
    token = session['access_token']
    tracks = topTracks(token)
    artists = topArtists(token)
    user_info = {
        'fav_artists' : artists,
        #'fav_tracks' : tracks
    }
    favorite_artists = []

    for i in user_info['fav_artists']['items']:
        favorite_artists.append(i['name'])

    return str(favorite_artists)

def topTracks(token):  
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
        user_data['top_tracks'].append({'song_name': song_name})

    return user_data

def topArtists(token):  
    headers = {
        'Authorization' : 'Bearer ' + token
    }
    params ={
        'time_range' : 'long_term',
        'limit' : '5'
    }
    response = requests.get('https://api.spotify.com/v1/me/top/artists', headers = headers, params=params)

    if response.status_code == 200:
        top_artists = response.json()
    else:
        error_data = response.json()

    return top_artists