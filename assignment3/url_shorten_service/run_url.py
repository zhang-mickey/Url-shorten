import json

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify, json
from werkzeug.datastructures import Headers

import services.validate_url as validate_url
from services.id_generator import IdGenerator
from services.mode import Mode
from url_db import *
import redis

from threading import Lock

app = Flask(__name__)

app.config['JSONIFY_MIMETYPE'] = 'application/json'

AUTH_SERVICE_URL = "http://auth_service:5001/verify-token"

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

recycling_pool = []
counter_lock = Lock()
counter = 0

shuffle = True
MODE = Mode.BASIC

id_generator = IdGenerator(shuffle=shuffle)


def check_expired_urls():
    global recycling_pool
    with connect_db() as conn:
        delete_expired_urls(conn)


scheduler = BackgroundScheduler()
scheduler.add_job(func=check_expired_urls, trigger="interval", seconds=30)
scheduler.start()

def verify_token(auth_header):
    """Send token to auth microservice for validation"""
    response = requests.post(AUTH_SERVICE_URL, json={"token": auth_header})
    if response.status_code == 200:
        return response.json()  # Expected to return user info if valid
    return None  # Invalid token


def get_authenticated_user(headers: Headers):
    auth_header = headers.get("Authorization")
    if not auth_header:
        return None, jsonify({"error": "Forbidden"})

    user_info = verify_token(auth_header)
    if not user_info:
        return None, jsonify({"error": "Invalid token"})

    user_name = user_info.get("username")
    if not user_name:
        return jsonify({"error": "Unauthorized"})

    return user_name, None  # 返回用户信息，如果认证失败则返回错误响应


@app.route("/", methods=["GET", "POST", "DELETE"])
def index():
    global counter
    # GET all stored URLs
    if request.method == "GET":
        _, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403

        with connect_db() as conn:
            if not conn:
                return jsonify({"error": "Fail to connect"}), 404
            urls = get_all(conn)

        if not urls:
            print("get_all but got None")
            return jsonify({"error": "No URLs found"}), 404

        return jsonify(urls), 200

    # DELETE all stored URLs
    if request.method == "DELETE":
        _, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403
        with connect_db() as conn:
            if not conn:
                return jsonify({"error": "Fail to connect"}), 404
            delete_all_urls()
            redis_client.flushdb()
        return jsonify({"message": "all urls deleted"}), 404

    if request.method == "POST":
        user_name, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403

        data = request.get_json()
        # response = requests.post(url, headers=self.headers, json={'value': str(url_to_shorten)})
        if not data or "value" not in data:
            return jsonify({"error": "Missing URL"}), 400
        original_url = data["value"].strip()
        # Validate URL
        if not validate_url.is_valid_url(original_url) or not validate_url.domain_exists(original_url):
            return jsonify({"error": "Invalid URL"}), 400

        expiry_time = data.get("expiry_time", None)
        # check used ID
        if recycling_pool:
            short_url = recycling_pool.pop()  # use the ID from pool
        else:
            with counter_lock:
                if MODE == Mode.LCG:
                    short_url = id_generator.lcg_encode(counter)  # if the pool is empty, generate new id
                else:
                    # DEFAULT SETTING
                    short_url = id_generator.base64_encode(counter)
                counter += 1

        with connect_db() as conn:
            if not conn:
                return jsonify({"error": "Fail to connect"}), 500

            add_url_mapping(conn, short_url, user_name, original_url, expiry_time)

            redis_client.setex(short_url, 3600, original_url)

            return jsonify({"id": short_url, "original_url": original_url, "expiry_time": expiry_time}), 201


def check_id(short_id):
    try:
        with connect_db() as conn:
            result = get_by_short_id(conn, short_id)
            return result
            # if not result:
            #     return None
            # return result['username']

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/<short_id>", methods=["GET", "PUT", "DELETE"])
def handle_short_url(short_id):
    # user_id = request.args.get('user_id', 'guest')
    if request.method == "GET":
        user_name, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403

        # Check Redis cache first
        cached_url = redis_client.get(short_id)
        if cached_url:
            print(f"Cache hit: {short_id} -> {cached_url}")
            return jsonify({"value": cached_url}), 301  # Redirect to cached URL
        with connect_db() as conn:
            result = get_by_short_id(conn, short_id)

        if result and result["user_id"] == user_name:
            return jsonify({"value": result["original_url"]}), 301

        return jsonify({"error": "Not Found"}), 404

    # PUT: Update URL
    if request.method == "PUT":

        user_name, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403

        raw_data = request.data.decode("utf-8")
        data = json.loads(raw_data)
        new_url = data.get("url")
        if not new_url:
            return jsonify({"error": "Missing URL"}), 400
        if not check_id(short_id):
            return jsonify({"error": "id not found"}), 404
        if not validate_url.is_valid_url(new_url) or not validate_url.domain_exists(new_url):
            print("------------I am here------------")
            return jsonify({"error": "Invalid URL"}), 400

        try:
            with connect_db() as conn:
                result = get_by_short_id(conn, short_id)
                if not result:
                    return jsonify({"error": "Short URL not found"}), 404

                db_user_id = result['user_id']
                if db_user_id != user_name:
                    return jsonify({"error": "Unauthorized"}), 403

                update_url_mapping(conn, short_id=short_id, new_original_url=new_url)
                redis_client.setex(short_id, 3600, new_url)

                return jsonify({"message": f"Short URL {short_id} updated successfully."}), 200
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    # Erase ID
    if request.method == "DELETE":

        user_name, error_response = get_authenticated_user(request.headers)
        if error_response:
            return error_response, 403

        with connect_db() as conn:
            deleted = delete_url_mapping(conn, short_id)
            print("---------------", deleted)
            if deleted:
                redis_client.delete(short_id)  # Remove from Redis
                return jsonify({"message": f"the URL {short_id} has been deleted"}), 204
        return jsonify({"error": "Not Found"}), 404


if __name__ == "__main__":
    setup_db(connect_db())
    app.run(debug=True, host="0.0.0.0", port=8000)
