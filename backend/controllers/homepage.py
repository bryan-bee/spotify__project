import requests
from flask import Blueprint, jsonify

from spotify_auth import NotAuthenticated, get_valid_access_token

homepage_controller = Blueprint('homepage', __name__)


# The frontend calls this once on load to find out whether the saved session
# cookie still maps to a usable (or refreshable) Spotify login, without
# triggering a browser redirect. 401 means "show the login screen".
@homepage_controller.route('/api/me', methods=['GET'])
def me():
    try:
        token = get_valid_access_token()
    except NotAuthenticated:
        return jsonify({'error': 'not_authenticated'}), 401

    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': 'Bearer ' + token},
    )
    if response.status_code != 200:
        return jsonify({'error': 'spotify_api_error'}), response.status_code

    profile = response.json()
    return jsonify({
        'display_name': profile.get('display_name'),
        'image_url': (profile.get('images') or [{}])[0].get('url'),
        'spotify_url': profile.get('external_urls', {}).get('spotify'),
    })
