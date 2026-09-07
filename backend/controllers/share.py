import json
import secrets
from datetime import datetime, timezone

import requests
from flask import Blueprint, jsonify, request

from db import get_connection
from spotify_auth import NotAuthenticated, get_valid_access_token
from controllers.topStuff import VALID_TIME_RANGES, SpotifyApiError, build_wrapped_stats

share_controller = Blueprint('share', __name__)


# Creates a public, read-only snapshot of the caller's current stats so it can
# be viewed by anyone with the link, without them needing a Spotify login.
@share_controller.route('/api/share', methods=['POST'])
def create_share():
    body = request.get_json(silent=True) or {}
    time_range = body.get('time_range', 'medium_term')
    if time_range not in VALID_TIME_RANGES:
        return jsonify({'error': 'invalid_time_range', 'valid_values': list(VALID_TIME_RANGES)}), 400

    try:
        token = get_valid_access_token()
    except NotAuthenticated:
        return jsonify({'error': 'not_authenticated'}), 401

    try:
        stats = build_wrapped_stats(token, time_range)
        display_name = _fetch_display_name(token)
    except SpotifyApiError as e:
        return jsonify({'error': 'spotify_api_error', 'detail': str(e)}), 502

    share_id = secrets.token_urlsafe(6)
    with get_connection() as conn:
        conn.execute(
            'INSERT INTO shared_wrapped (id, created_at, display_name, data) VALUES (?, ?, ?, ?)',
            (share_id, datetime.now(timezone.utc).isoformat(), display_name, json.dumps(stats)),
        )

    return jsonify({'share_id': share_id})


# Public endpoint, deliberately not behind get_valid_access_token: this is
# what lets a snapshot be opened by someone who was never logged in.
@share_controller.route('/api/share/<share_id>', methods=['GET'])
def get_share(share_id):
    with get_connection() as conn:
        row = conn.execute(
            'SELECT created_at, display_name, data FROM shared_wrapped WHERE id = ?',
            (share_id,),
        ).fetchone()

    if row is None:
        return jsonify({'error': 'not_found'}), 404

    stats = json.loads(row['data'])
    return jsonify({
        'created_at': row['created_at'],
        'display_name': row['display_name'],
        **stats,
    })


def _fetch_display_name(token):
    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': 'Bearer ' + token},
    )
    if response.status_code != 200:
        raise SpotifyApiError(f'me returned {response.status_code}')
    return response.json().get('display_name')
