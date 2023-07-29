from flask_session import Session
from flask import Flask, session
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Apply CORS middleware to allow requests from all origins
from dotenv import load_dotenv
load_dotenv()
from controllers.homepage import homepage_controller
from controllers.login import login_controller
from controllers.logout import logout_controller

# Configure the Flask Session
app.config['SESSION_TYPE'] = 'filesystem'

# Register the 'authenticate' controller
app.register_blueprint(homepage_controller)
app.register_blueprint(login_controller)
app.register_blueprint(logout_controller)

Session(app)

if __name__ == '__main__':
    app.run(debug=True)