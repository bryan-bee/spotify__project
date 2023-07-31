import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, jsonify, session, redirect, url_for
import time
import requests
import os

topStuff_controller = Blueprint('topStuff', __name__)

#favorite_songs is a list of dictionaries. index 1-10 each dictionary represents 1 song where key is song and value is artist
#favorite_artists is a list of dictionaries containing name, url , and genre of those artists
#artist_names , artist_urls are lists of those individuals


@topStuff_controller.route('/api/topStuff', methods=['GET', 'POST'])
def topStuff():
    if 'access_token' not in session or session['access_token'] == None:
        return redirect(url_for('login.login'))
    token = session['access_token']
    tracks = topTracks(token)
    artistsDict = topArtists(token)

    favorite_artists = []
    artist_names = []
    artist_urls = []
    favorite_genres = {}
    favorite_songs = []

    for i in artistsDict['items']:
        artist_name = i['name']
        artist_pic_url = i['images'][0]     
        genres = i['genres']    

        dict = {
            'name': artist_name,
            'url' : artist_pic_url,
            'genres' : genres
        }
        favorite_artists.append(dict)
    
    for i in favorite_artists:
        artist_names.append(i['name'])
        artist_urls.append(i['url'])
        for genre in i['genres']:
            if genre in favorite_genres:
                favorite_genres[genre] +=1
            else:
                favorite_genres[genre] =1
    #artist_names favorite_genres artist_urls

    for track in tracks['top_tracks']:
        favorite_songs.append({track['song_name'] : track['artists']})
    
    best_genre = max(favorite_genres.items(), key=lambda item: item[1])


    all_info = {
        'favorite_songs' : favorite_songs,
        'favorite_artists' : favorite_artists,
        'favorite_genres' : favorite_genres,
        'best_genre' : best_genre,


    }
    return  all_info



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
        artists = ', '.join([artist['name'] for artist in track['artists']])
        user_data['top_tracks'].append({'song_name': song_name, 'artists': artists})

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