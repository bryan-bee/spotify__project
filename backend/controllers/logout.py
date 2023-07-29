from flask import Blueprint, session, redirect, url_for

logout_controller = Blueprint('logout', __name__)

@logout_controller.route('/api/logout', methods=['GET','POST'])
def logout():
    # Clear the access token from the session
    session.pop('access_token', None)
    session.clear()
    return redirect(url_for('login.login'))  # Redirect to the login page after logout
