import os
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)

# SECRET_KEY must be stable across restarts, or every existing session cookie
# becomes unverifiable (and therefore unusable) the moment the server reloads.
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is not set in .env")

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

# Server-side sessions: only an opaque session id sits in the browser cookie,
# the access/refresh tokens themselves stay on disk here, not on the client.
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.path.dirname(__file__), "flask_session")
app.config["SESSION_PERMANENT"] = True
Session(app)

# The frontend runs on a different origin (React dev server) and needs to send
# the session cookie with each request, so credentials must be explicitly allowed.
CORS(app, supports_credentials=True, origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")])

from controllers.homepage import homepage_controller
from controllers.login import login_controller
from controllers.logout import logout_controller
from controllers.topStuff import topStuff_controller

app.register_blueprint(homepage_controller)
app.register_blueprint(login_controller)
app.register_blueprint(logout_controller)
app.register_blueprint(topStuff_controller)

if __name__ == '__main__':
    app.run(debug=True)
