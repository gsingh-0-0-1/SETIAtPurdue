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
import mysql.connector as mysql
import os
import json


ALL_AFFILS = {
        "Purdue University": "purdue.edu",
        "SETI Institute": "seti.org"
}

def match_email_affil(email, affil):
    return email.endswith(ALL_AFFILS[affil])

cnx = mysql.connect(
        user='root',
        password=os.environ.get("MYSQL_ROOT_PASSWORD"),
        database='mysql',
        host='cseti-mysql',
        port=3306
    )

cursor = cnx.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS userpass(user VARCHAR(255) PRIMARY KEY, pwhash VARCHAR(255))")
cursor.execute("""CREATE TABLE IF NOT EXISTS userinfo(
    user VARCHAR(255) PRIMARY KEY,
    fullname VARCHAR(255),
    email VARCHAR(255),
    affil VARCHAR(255)
    )
""")
cursor.close()

USERPASSDB = {}

app = Flask(__name__,
	static_folder='./static'
)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds = 24 * 60 * 60)
REFRESH_MINUTES = 120

def get_user_pwhash(user):
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT pwhash
        FROM userpass
        WHERE user=%(user)s
    """, {
        'user': user
    })
    pwhash = cursor.fetchall()[0][0]
    cursor.close()
    return pwhash

def get_user_info(user):
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT user, fullname, email, affil
        FROM userinfo
        WHERE user=%(user)s
    """, {
        'user': user
    })
    result = cursor.fetchall()[0]
    cursor.close()
    return {
        "user": user,
        "fullname" : result[1],
        "email": result[2],
        "affil": result[3]
    }

def create_new_user(user, pwhash, fullname, email, affil):
    cursor = cnx.cursor()
    cursor.execute("""
        INSERT INTO userpass
        VALUES
        (%(user)s, %(pwhash)s)
    """, {
        'user': user,
        'pwhash': pwhash
    })
    cursor.execute("""
        INSERT INTO userinfo
        VALUES
        (
            %(user)s,
            %(fullname)s,
            %(email)s,
            %(affil)s
        )
    """, {
        'user': user,
        'fullname': fullname,
        'email': email,
        'affil': affil
    })
    cnx.commit()
    cursor.close()

def check_user_exists(user):
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT COUNT(1)
        FROM userpass
        WHERE user=%(user)s
    """, {
        'user': user
    })
    print("checking user " + user + " exists")
    result = cursor.fetchall()
    print(result)
    if result[0][0] == 0:
        cursor.close()
        return False
    cursor.close()
    return True

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

    if check_user_exists(username):
        return "Username already in use", 400

    pwhash = generate_password_hash(password)

    #USERPASSDB[username] = pwhash

    create_new_user(username, pwhash, fullname, email, affil)

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

    if not check_user_exists:
        return "Invalid username or password", 400

    

    if not check_password_hash(get_user_pwhash(username), password):
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
    return json.dumps(get_user_info(current_user))

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
