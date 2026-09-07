import requests
from flask import Blueprint, jsonify, request

from spotify_auth import NotAuthenticated, get_valid_access_token

topStuff_controller = Blueprint('topStuff', __name__)

# Spotify's own time_range buckets, mapped to labels the frontend can show directly.
VALID_TIME_RANGES = {
    'short_term': 'Last 4 Weeks',
    'medium_term': 'Last 6 Months',
    'long_term': 'All Time',
}


@topStuff_controller.route('/api/topStuff', methods=['GET'])
def topStuff():
    time_range = request.args.get('time_range', 'medium_term')
    if time_range not in VALID_TIME_RANGES:
        return jsonify({'error': 'invalid_time_range', 'valid_values': list(VALID_TIME_RANGES)}), 400

    try:
        token = get_valid_access_token()
    except NotAuthenticated:
        return jsonify({'error': 'not_authenticated'}), 401

    try:
        stats = build_wrapped_stats(token, time_range)
    except SpotifyApiError as e:
        return jsonify({'error': 'spotify_api_error', 'detail': str(e)}), 502

    return jsonify(stats)


class SpotifyApiError(Exception):
    pass


def build_wrapped_stats(token, time_range):
    """Fetch top tracks/artists for a given Spotify time_range and shape them
    into the payload both the dashboard and the public share page render."""
    tracks = _fetch_top_tracks(token, time_range)
    artists = _fetch_top_artists(token, time_range)

    favorite_artists = []
    favorite_genres = {}

    for artist in artists['items']:
        images = artist.get('images') or []
        favorite_artists.append({
            'name': artist['name'],
            'url': images[0]['url'] if images else None,
            'genres': artist['genres'],
        })
        for genre in artist['genres']:
            favorite_genres[genre] = favorite_genres.get(genre, 0) + 1

    favorite_songs = [
        {'song_name': track['song_name'], 'artists': track['artists']}
        for track in tracks
    ]

    best_genre = max(favorite_genres.items(), key=lambda item: item[1])[0] if favorite_genres else None

    return {
        'time_range': time_range,
        'time_range_label': VALID_TIME_RANGES[time_range],
        'favorite_songs': favorite_songs,
        'favorite_artists': favorite_artists,
        'favorite_genres': favorite_genres,
        'best_genre': best_genre,
    }


def _fetch_top_tracks(token, time_range):
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks',
        headers={'Authorization': 'Bearer ' + token},
        params={'time_range': time_range, 'limit': 10},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'top/tracks returned {response.status_code}')

    return [
        {
            'song_name': track['name'],
            'artists': ', '.join(artist['name'] for artist in track['artists']),
        }
        for track in response.json()['items']
    ]


def _fetch_top_artists(token, time_range):
    response = requests.get(
        'https://api.spotify.com/v1/me/top/artists',
        headers={'Authorization': 'Bearer ' + token},
        params={'time_range': time_range, 'limit': 5},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'top/artists returned {response.status_code}')

    return response.json()
