import datetime

from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect
from flask import render_template

from flask_jwt_extended import get_jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

from werkzeug.security import generate_password_hash, check_password_hash

USERPASSDB = {}

app = Flask(__name__,
	static_folder='./static'
)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds = 60)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes = 30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity = get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@jwt.unauthorized_loader
@jwt.invalid_token_loader
@jwt.expired_token_loader
def redirect_to_login(*args):
    return redirect("/login")

@app.route("/signup_request", methods=["POST"])
def signup_request():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
    	return "No username or password provided", 400

    if username in USERPASSDB:
        return "Username already in use", 400

    pwhash = generate_password_hash(password)

    USERPASSDB[username] = pwhash

    access_token = create_access_token(
        identity = username,
    )
    response = jsonify({
        "msg": "signup successful",
        "userid": username,
    })
    set_access_cookies(response, access_token)
    return response


@app.route("/login_request", methods=["POST"])
def login_request():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return "No username or password provided", 400

    if username not in USERPASSDB:
        return "Invalid username or password", 400

    if not check_password_hash(USERPASSDB[username], password):
        return "Invalid username or password", 400

    access_token = create_access_token(
        identity = username,
    )

    response = jsonify({
        "msg": "login successful",
        "userid": username,
    })
    set_access_cookies(response, access_token)
    return response

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required(locations=["cookies"])
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/", methods = ["GET"])
def main():
    return render_template("home.html")

@app.route("/signup", methods = ["GET"])
def signup_page():
    return render_template("signup.html")

@app.route("/login", methods = ["GET"])
def login_page():
    return render_template("login.html")

@app.route("/ping", methods = ["GET"])
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 80, debug = True)
