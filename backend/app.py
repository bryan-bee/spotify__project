import os
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

# In production, this same Flask process also serves the already-built React
# app (see the catch-all route at the bottom) - one origin for everything,
# which is what sidesteps the whole CORS/cookie-host-mismatch class of bugs
# hit repeatedly during local dev (see STUDY_NOTES.md §6, §7, §29). Locally,
# the frontend still runs separately via `npm start` on port 3000, and this
# folder simply won't exist yet unless `npm run build` has been run.
#
# static_folder points specifically at build/static (not the whole build
# directory) with static_url_path="/static", matching the exact "/static/js/
# main.xxx.js" paths index.html itself references. Pointing static_folder at
# the whole build dir with static_url_path="" instead looks simpler, but it
# makes Flask register its own automatic static route at "/<path:filename>" -
# the identical pattern to the catch-all route below - and Flask's built-in
# one wins that conflict (registered first, during Flask(__name__, ...) -
# silently 404ing on every client-side route (e.g. /dashboard) before the
# catch-all ever runs, since Werkzeug doesn't try a second rule after the
# first match already produced a response.
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
FRONTEND_STATIC_DIR = os.path.join(FRONTEND_BUILD_DIR, 'static')

app = Flask(__name__, static_folder=FRONTEND_STATIC_DIR, static_url_path='/static')

# Render (like most PaaS platforms) terminates HTTPS at its own edge proxy
# and forwards requests to this container over plain HTTP internally - so
# without this, request.scheme reports "http" even when the browser used
# "https", which broke login.py's dynamically-built redirect_uri (it came
# out as http://..., not matching the https:// URI registered with
# Spotify). The proxy does send an X-Forwarded-Proto header saying what the
# real original scheme was; ProxyFix tells Flask to trust and use it.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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

# Only needed for local dev, where the React dev server (port 3000) is a
# different origin from Flask (port 5000) and needs to send the session
# cookie with each request - credentials must be explicitly allowed, and
# explicitly, since a wildcard origin can't be combined with credentials
# (see STUDY_NOTES.md §7). In production this app serves its own frontend
# from the same origin, so no cross-origin request (and therefore no CORS
# check) is even involved - this is harmless to leave enabled either way.
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


# Registered last so Werkzeug's routing always tries the specific /api/*
# and /static/* rules above first - this only catches whatever's left over:
# root-level build files (favicon.ico, manifest.json, ...) get served
# directly, and any real client-side route (e.g. /dashboard, /share/xyz),
# which has no matching file on disk at all, falls through to index.html so
# React Router can take over from there - the same "SPA fallback" behavior
# the CRA dev server's proxy gave for free during local development.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    full_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if path and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_BUILD_DIR, path)
    return send_from_directory(FRONTEND_BUILD_DIR, 'index.html')


if __name__ == '__main__':
    # host="0.0.0.0" binds to every network interface, not just the loopback
    # one - Flask's default (127.0.0.1 only) would otherwise refuse
    # connections from another device on the LAN (a phone) entirely, before
    # any of the redirect_uri/CORS logic above even gets a chance to run.
    app.run(host='0.0.0.0', debug=True)
