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

from dotenv import load_dotenv
import os
import json
import random

import src.mail.mail as mail
from src.sql.client import MySQLClient
from src.helpers import match_email_affil, random_string_token
from src.constants import ALL_AFFILS

from api import api_blueprint
from training import train_blueprint

MYSQL_CLIENT = MySQLClient()

app = Flask(__name__,
	static_folder='./static'
)

app.register_blueprint(api_blueprint)
app.register_blueprint(train_blueprint)


# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds = 24 * 60 * 60)
REFRESH_MINUTES = 120

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes = REFRESH_MINUTES))
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

@app.route("/confirmaccount/<string:conftoken>")
def confirmaccount(conftoken):
    if not conftoken:
        return redirect("/login")

    user = MYSQL_CLIENT.get_user_from_conftoken(conftoken)
    if not user:
        return redirect("/signup")

    MYSQL_CLIENT.confirm_user(user)

    access_token = create_access_token(
        identity = user,
    )

    response = redirect("/profile")

    set_access_cookies(response, access_token)

    return response

@app.route("/signup_request", methods=["POST"])
def signup_request():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    affil = request.json.get("affil", None)
    email = request.json.get("email", None)
    fullname = request.json.get("fullname", None)

    if not username or not password:
    	return "No username or password provided", 400

    if affil not in ALL_AFFILS.keys():
        return "No valid affiliation provided!", 400

    if not match_email_affil(email, affil):
        return "Email must match affiliation!", 400

    if not fullname:
        return "No full name provided", 400

    if MYSQL_CLIENT.check_user_exists(username):
        return "Username already in use", 400

    pwhash = generate_password_hash(password)

    conftoken = random_string_token(255)
    MYSQL_CLIENT.create_new_user(username, pwhash, fullname, email, affil, conftoken)
    mail.send_confirmation_email(fullname, email, conftoken)

    #access_token = create_access_token(
    #    identity = username,
    #)
    response = "Success", 200
    #set_access_cookies(response, access_token)
    return response


@app.route("/wait_for_conf")
def wait_for_conf():
    return render_template('confirm.html')

@app.route("/login_request", methods=["POST"])
def login_request():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return "No username or password provided", 400

    if not MYSQL_CLIENT.check_user_exists(username):
        return "Invalid username or password", 400

    user_pwhash = MYSQL_CLIENT.get_user_pwhash(username)
    if not user_pwhash:
        return "Please confirm your account via the link sent to your email!", 400

    if not check_password_hash(user_pwhash, password):
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

@app.route("/profile", methods=["GET"])
@jwt_required(locations=["cookies"])
def profile():
    return render_template("profile.html")

@app.route("/whoami", methods=["GET"])
@jwt_required(locations=["cookies"])
def whoami():
    current_user = get_jwt_identity()
    return json.dumps(MYSQL_CLIENT.get_user_info(current_user))

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

@app.route("/all_affils", methods = ["GET"])
def all_affils():
    return json.dumps(
            {
                "data" : list(ALL_AFFILS.keys())
            }
    )

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 80, debug = True)
