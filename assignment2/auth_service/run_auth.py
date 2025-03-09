import base64
import hashlib
import hmac
import json
import time

from flask import Flask, request, jsonify, json

from auth_db import *

# from assignment2.auth_service.auth_db import *

PRIVATE_KEY = "groupzhang"
ALGORITHM = "HS256"  # HMAC with SHA-256

app = Flask(__name__)


def generate_password_hash(password):
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + hashed_password.hex()  # 存储格式：salt:hash


def check_password_hash(hashed_password, password):
    salt, stored_hash = hashed_password.split(":")
    salt = bytes.fromhex(salt)
    hashed_attempt = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_attempt.hex() == stored_hash


def base64url_encode(data):
    """Encodes data to Base64 URL-safe format"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def base64url_decode(data):
    """Decodes Base64 URL-safe format"""
    padding = 4 - (len(data) % 4)
    return base64.urlsafe_b64decode(data + "=" * padding)


# JWT默认不加密
# Header:Json 对象，描述JWT的元数据
# Payload：Json对象，存放实际需要传递的数据，「exp，sub」等，要用Base64URL算法转成字符串
# Signature：对前两部分的签名

def create_jwt(payload, secret=PRIVATE_KEY):
    header = {"alg": ALGORITHM, "typ": "JWT"}

    # Convert to JSON and encode to Base64 URL-safe
    header_enc = base64url_encode(json.dumps(header).encode("utf-8"))
    payload_enc = base64url_encode(json.dumps(payload).encode("utf-8"))

    # Create signature
    signature = hmac.new(
        secret.encode("utf-8"),
        f"{header_enc}.{payload_enc}".encode("utf-8"),
        hashlib.sha256
    ).digest()

    signature_enc = base64url_encode(signature)

    return f"{header_enc}.{payload_enc}.{signature_enc}"


def verify_jwt(token, secret=PRIVATE_KEY):
    try:
        header_enc, payload_enc, signature_enc = token.split(".")
        # Recreate signature to compare
        signature_check = hmac.new(
            secret.encode("utf-8"),
            f"{header_enc}.{payload_enc}".encode("utf-8"),
            hashlib.sha256
        ).digest()

        if base64url_encode(signature_check) != signature_enc:
            return None  # Invalid signature

        # Decode payload
        payload = json.loads(base64url_decode(payload_enc))

        # Check token expiration
        if "exp" in payload and payload["exp"] < time.time():
            return None  # Token expired

        return payload  # Return decoded payload (user identity)

    except Exception as e:
        print("token verified failed", e)
        return None  # Invalid token format


@app.route("/users", methods=["POST"])
def register_user():
    # check Nginx
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(f"Request received from IP: {client_ip}")
    host = request.headers.get("Host")
    print(f"Request forwarded by Nginx with Host: {host}")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    password = generate_password_hash(password)

    if not username or not password:
        return jsonify({"error": "Require username and password"}), 400

    with connect_db() as conn:
        if conn is None:
            return jsonify({"error": "Fail to connect"}), 500
        try:
            existing_user = get_user(conn, username)
            if existing_user:
                return jsonify({"error": "duplicate"}), 409
            else:
                user_id = add_user(conn, username, password)[0]
                return jsonify({"message": "Successful", "user_id": user_id}), 201
        except psycopg2.Error as e:
            print(f"wrong operation: {e}")
            return jsonify({"error": "wrong operation"}), 500


@app.route("/users", methods=["PUT"])
def update_password():
    """Update user password if old password is correct"""
    data = request.get_json()
    username = data.get("username")
    old_password = data.get("old-password")
    new_password = data.get("new-password")

    if not username or not old_password or not new_password:
        return jsonify({"error": "Missing fields"}), 400

    with connect_db() as conn:
        if conn is None:
            return jsonify({"error": "Fail to connect"}), 500
        result = get_password(conn, username)
        if result:
            hashed_password = result[0]
            if not check_password_hash(hashed_password, old_password):
                return jsonify({"error": "Forbidden"}), 403

            new_hashed_password = generate_password_hash(new_password)
            update_user(conn, username, new_hashed_password)
            return jsonify({"message": "Password updated successfully"}), 200
        else:
            return jsonify({"error": "Forbidden"}), 403


@app.route("/users/login", methods=["POST"])
def login():
    """Authenticate user and return JWT"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    with connect_db() as conn:
        if conn is None:
            return jsonify({"error": "Fail to connect"}), 500

        result = get_password(conn, username)
        if result is None:
            return jsonify({"error": "user do not exist"}), 403

        hashed_password = result[0]
        if not check_password_hash(hashed_password, password):
            return jsonify({"error": "wrong password"}), 403

        payload = {
            "username": username,
            "exp": time.time() + 600
        }
        token = create_jwt(payload)
        return jsonify({"token": token}), 200


@app.route("/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json()
    if not data["token"]:
        return ""
    return jsonify(verify_jwt(token=data["token"], secret=PRIVATE_KEY)), 200


if __name__ == "__main__":
    # create_tables()
    setup_db(connect_db())
    app.run(debug=True, host="0.0.0.0", port=5001)
