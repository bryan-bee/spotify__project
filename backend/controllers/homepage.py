from flask import Blueprint, jsonify, session, redirect, url_for
import requests

homepage_controller = Blueprint('homepage', __name__)

# Spotify API base URL
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1/'

@homepage_controller.route('/api/homepage', methods=['GET'])
def homepage():
    if 'access_token' in session:
        try:
            access_token = session['access_token']

            # Make a request to the Spotify API to get the user's info
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(f'{SPOTIFY_API_BASE_URL}me', headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                user_info = response.json()
                return jsonify(user_info)
            else:
                # Handle the case where the request failed
                return jsonify({'error': 'Failed to fetch user info'}), 500
        except Exception as e:
            # Handle any other exceptions that may occur
            print(e)
            return jsonify({'error': 'An error occurred'}), 500
    else:
        # If the user is not authenticated, redirect to the login page
        return redirect(url_for('login.login'))
