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
# the session cookie with each request, so credentials must be explicitly
# allowed - and explicitly, since a wildcard origin can't be combined with
# credentials (see STUDY_NOTES.md §7). Listing both 127.0.0.1 (desktop) and
# the LAN IP (a phone on the same WiFi) lets both be tested without editing
# this every time you switch devices.
default_origins = "http://127.0.0.1:3000,http://192.168.68.62:3000"
FRONTEND_ORIGINS = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", default_origins).split(",")]
CORS(app, supports_credentials=True, origins=FRONTEND_ORIGINS)

from db import init_db
from controllers.homepage import homepage_controller
from controllers.login import login_controller
from controllers.logout import logout_controller
from controllers.topStuff import topStuff_controller
from controllers.share import share_controller

init_db()

app.register_blueprint(homepage_controller)
app.register_blueprint(login_controller)
app.register_blueprint(logout_controller)
app.register_blueprint(topStuff_controller)
app.register_blueprint(share_controller)

if __name__ == '__main__':
    # host="0.0.0.0" binds to every network interface, not just the loopback
    # one - Flask's default (127.0.0.1 only) would otherwise refuse
    # connections from another device on the LAN (a phone) entirely, before
    # any of the redirect_uri/CORS logic above even gets a chance to run.
    app.run(host='0.0.0.0', debug=True)
