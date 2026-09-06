from flask import Blueprint, jsonify, session

logout_controller = Blueprint('logout', __name__)


@logout_controller.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})
