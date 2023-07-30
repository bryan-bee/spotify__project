from flask import Flask, session
from flask_cors import CORS, cross_origin
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)  # Apply CORS middleware to allow requests from all origin
from dotenv import load_dotenv
load_dotenv()
from controllers.homepage import homepage_controller
from controllers.login import login_controller
from controllers.logout import logout_controller

# Register the 'authenticate' controller
app.register_blueprint(homepage_controller)
app.register_blueprint(login_controller)
app.register_blueprint(logout_controller)

if __name__ == '__main__':
    app.run(debug=True)