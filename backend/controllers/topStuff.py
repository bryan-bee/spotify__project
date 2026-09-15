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
    market = _fetch_user_market(token)

    favorite_artists = []
    favorite_genres = {}

    for rank_index, artist in enumerate(artists['items']):
        images = artist.get('images') or []
        popularity = artist.get('popularity')
        favorite_artists.append({
            'id': artist['id'],
            'name': artist['name'],
            'url': images[0]['url'] if images else None,
            'genres': artist['genres'],
            'popularity': popularity,
            'estimated_top_percent': _estimate_top_listener_percent(popularity, rank_index),
        })
        for genre in artist['genres']:
            favorite_genres[genre] = favorite_genres.get(genre, 0) + 1

    favorite_songs = [
        {
            'id': track['id'],
            'song_name': track['song_name'],
            'artists': track['artists'],
        }
        for track in tracks
    ]

    best_genre = max(favorite_genres.items(), key=lambda item: item[1])[0] if favorite_genres else None

    previews = _build_previews(token, market, tracks, favorite_artists, best_genre)

    return {
        'time_range': time_range,
        'time_range_label': VALID_TIME_RANGES[time_range],
        'favorite_songs': favorite_songs,
        'favorite_artists': favorite_artists,
        'favorite_genres': favorite_genres,
        'best_genre': best_genre,
        'previews': previews,
    }


def _estimate_top_listener_percent(popularity, rank_index):
    """A clearly-labeled ESTIMATE, not real Spotify data - the public Web API has no
    endpoint that reveals a user's actual percentile rank among an artist's listeners
    (that's Spotify's own internal analytics, and it's what the real Spotify Wrapped
    uses; third-party apps can't get it). This derives a plausible-feeling number from
    two real, available signals instead:

    - `popularity` (Spotify's own real 0-100 artist popularity score): a more
      mainstream artist has a much larger total listener base, so being a fan of one
      is statistically less rare than being a fan of a niche artist with few listeners
      - a lower popularity score produces a smaller (more impressive) baseline.
    - `rank_index` (this artist's real rank, 0-based, among the user's own top
      artists for this period): ranking as someone's #1 most-played artist is a
      stronger fan signal than ranking 5th, so each step down adds a flat penalty.

    The frontend must label this "Est." - it is a fun approximation, not a fact about
    the artist's real global listener base.
    """
    baseline = max(0.5, round((100 - (popularity or 0)) / 2, 2))
    return min(round(baseline + rank_index * 3, 2), 99.99)


def _build_previews(token, market, top_tracks, favorite_artists, best_genre):
    """Pick one clip each for the top-song, top-artist, and top-genre cards,
    making sure no two of those three clips are the same track. These play
    via Spotify's embed player (WrappedCards.js), which only needs a
    track id - not the (restricted, usually-null - see STUDY_NOTES.md §25)
    preview_url field - so picking here is purely about avoiding duplicates,
    not about finding a playable preview."""
    used_ids = set()
    previews = {'top_song': None, 'top_artist': None, 'top_genre': None}

    # Slot 1: the user's own #1 top track. This one is never substituted -
    # swapping in a different song would misrepresent what's actually the
    # top track.
    if top_tracks:
        top = top_tracks[0]
        previews['top_song'] = _preview_payload(top['id'], top['song_name'], top['artists'], top.get('preview_url'))
        used_ids.add(top['id'])

    # Slot 2: the most popular (by Spotify's own ranking) track by the
    # user's #1 top artist, that isn't already the top_song track.
    artist_track_cache = {}
    if favorite_artists:
        top_artist = favorite_artists[0]
        candidates = _fetch_artist_top_tracks(token, top_artist['id'], market)
        artist_track_cache[top_artist['id']] = candidates
        picked = _pick_unused_track(candidates, used_ids)
        if picked:
            previews['top_artist'] = _preview_payload(
                picked['id'], picked['name'], top_artist['name'], picked.get('preview_url')
            )
            used_ids.add(picked['id'])

    # Slot 3: a track by the highest-ranked artist that actually has the
    # user's #1 genre, so the clip played genuinely matches what's on screen.
    if best_genre:
        genre_artist = next((a for a in favorite_artists if best_genre in a['genres']), None)
        if genre_artist:
            candidates = artist_track_cache.get(genre_artist['id'])
            if candidates is None:
                candidates = _fetch_artist_top_tracks(token, genre_artist['id'], market)
            picked = _pick_unused_track(candidates, used_ids)
            if picked:
                previews['top_genre'] = _preview_payload(
                    picked['id'], picked['name'], genre_artist['name'], picked.get('preview_url')
                )
                used_ids.add(picked['id'])

    return previews


def _pick_unused_track(candidates, used_ids):
    for track in candidates:
        if track['id'] not in used_ids:
            return track
    return None


def _preview_payload(track_id, track_name, artist_name, preview_url):
    return {
        'track_id': track_id,
        'track_name': track_name,
        'artist_name': artist_name,
        'preview_url': preview_url,
    }


def _fetch_top_tracks(token, time_range):
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks',
        headers={'Authorization': 'Bearer ' + token},
        params={'time_range': time_range, 'limit': 5},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'top/tracks returned {response.status_code}')

    return [
        {
            'id': track['id'],
            'song_name': track['name'],
            'artists': ', '.join(artist['name'] for artist in track['artists']),
            'preview_url': track.get('preview_url'),
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


def _fetch_artist_top_tracks(token, artist_id, market):
    response = requests.get(
        f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks',
        headers={'Authorization': 'Bearer ' + token},
        params={'market': market},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'artists/{artist_id}/top-tracks returned {response.status_code}')

    return [
        {'id': track['id'], 'name': track['name'], 'preview_url': track.get('preview_url')}
        for track in response.json()['tracks']
    ]


def _fetch_user_market(token):
    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': 'Bearer ' + token},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'me returned {response.status_code}')
    return response.json().get('country') or 'US'
