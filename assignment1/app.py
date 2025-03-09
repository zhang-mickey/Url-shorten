import json
import time

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify, json

import services.validate_url as validate_url
from services.id_generator import IdGenerator
from services.mode import Mode

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json'

# Store URLs in memory
urls = {}
recycling_pool = []
counter = 0

shuffle = True
MODE = Mode.BASIC

id_generator = IdGenerator(shuffle=shuffle)


def check_expired_urls():
    global urls, recycling_pool
    current_time = time.time()
    expired_urls = []

    for user_id, user_urls in urls.items():
        for short_id, data in list(user_urls.items()):
            if "expiry_time" in data and data["expiry_time"] and data["expiry_time"] < current_time:
                print(f"URL {short_id} has expired.")
                expired_urls.append((user_id, short_id))

    for user_id, short_id in expired_urls:
        del urls[user_id][short_id]  # delete expired url
        recycling_pool.append(short_id)  # recycle
        print('The pool:', recycling_pool)


scheduler = BackgroundScheduler()
scheduler.add_job(func=check_expired_urls, trigger="interval", seconds=5)
scheduler.start()


@app.route("/", methods=["GET", "POST", "DELETE"])
def index():
    global counter
    # GET all stored URLs
    if request.method == "GET":
        if not urls:
            return jsonify({"error": "No URLs found"}), 404

        result = []
        for user_id, user_urls in urls.items():
            for short_id, data in user_urls.items():
                result.append({
                    "user_id": user_id,
                    "id": short_id,
                    "url": data["original_url"]
                })

        return jsonify(result), 200

    # DELETE all stored URLs
    if request.method == "DELETE":
        # user_id = request.args.get('user_id', 'guest')
        # if user_id in urls:
        urls.clear()
        recycling_pool.clear()
        counter = 0
        return jsonify({"value": None}), 404
        # return jsonify({"error": "No URLs found for user"}), 404

    # POST (shorten URL)
    if request.method == "POST":
        data = request.get_json()
        if not data or "value" not in data:
            return jsonify({"error": "Missing URL"}), 400

        user_id = data.get("user_id", "guest")
        original_url = data["value"].strip()
        duration = data.get("expiry_time", None)

        # Validate URL
        if not validate_url.is_valid_url(original_url) or not validate_url.domain_exists(original_url):
            return jsonify({"error": "Invalid URL"}), 400

        if duration:
            try:
                expiry_duration = float(duration)
                expiry_time = time.time() + expiry_duration
                print(expiry_time)
            except ValueError:
                return jsonify({"error": "Invalid expiration time"}), 400
        else:
            expiry_time = None

        # check used ID
        if recycling_pool:
            short_url = recycling_pool.pop()  # use the ID from pool
        else:
            if MODE == Mode.LCG:
                short_url = id_generator.lcg_encode(counter)  # if the pool is empty, generate new id
            else:
                # DEFAULT SETTING
                short_url = id_generator.base64_encode(counter)
            counter += 1

        urls.setdefault(user_id, {})[short_url] = {
            "original_url": original_url,
            "expiry_time": expiry_time
        }
        # print("Current URLs:", urls)
        # return jsonify(urls),201
        return jsonify({"id": short_url}), 201


@app.route("/<short_id>", methods=["GET", "PUT", "DELETE"])
def handle_short_url(short_id):
    user_id = request.args.get('user_id', 'guest')  # default to guest if no user_id is provided
    # print('user_id:', user_id)
    # GET: Redirect to original URL
    if request.method == "GET":
        # result = urls.get(short_id)
        user_urls = urls.get(user_id)
        # return jsonify(urls),200
        # return jsonify(user_urls), 200
        if user_urls is None:
            return jsonify({"error": "User not found"}), 404
        result = user_urls.get(short_id)
        if result:
            return jsonify({"value": result["original_url"]}), 301
        return jsonify({"error": "Not Found"}), 404

    # PUT: Update URL
    if request.method == "PUT":
        user_urls = urls.get(user_id)
        if not user_urls:
            return jsonify({"error": "User not found"}), 404

        if short_id not in user_urls:
            return jsonify({"error": "Not Found"}), 404

        raw_data = request.data.decode("utf-8")
        data = json.loads(raw_data)

        new_url = data.get("url")

        if not validate_url.is_valid_url(new_url) or not validate_url.domain_exists(new_url):
            return jsonify({"error": "Invalid URL"}), 400

        # Update URL
        user_urls[short_id]["original_url"] = new_url
        return "", 200

    # DELETE: Remove short URL
    if request.method == "DELETE":
        user_urls = urls.get(user_id)
        if not user_urls:
            return jsonify({"error": "User not found"}), 404

        if short_id in user_urls:
            del user_urls[short_id]
            recycling_pool.append(short_id)  # put the deleted id into the pool
            print('recycling pool', recycling_pool)
            return "", 204
        return jsonify({"error": "Not Found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
