
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=3000,
    connectTimeoutMS=3000,
    appname="FlaskScale",
)

db = client["flask_db"]
collection = db["data"]


@app.get("/")
def index():
    return (
        "Welcome to FlaskScale! Current UTC time: "
        + datetime.now(timezone.utc).isoformat(),
        200,
    )


@app.get("/healthz")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/ready")
def readiness():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ready"}), 200
    except PyMongoError:
        app.logger.exception("MongoDB readiness check failed")
        return jsonify({"status": "not_ready"}), 503


@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict) or not payload:
            return jsonify({
                "error": "A non-empty JSON object is required"
            }), 400

        try:
            result = collection.insert_one(payload)
            return jsonify({
                "status": "Data inserted",
                "id": str(result.inserted_id),
            }), 201
        except PyMongoError:
            app.logger.exception("MongoDB insert failed")
            return jsonify({
                "error": "Database operation failed"
            }), 503

    try:
        documents = list(
            collection.find({}, {"_id": 0}).limit(100)
        )
        return jsonify(documents), 200
    except PyMongoError:
        app.logger.exception("MongoDB read failed")
        return jsonify({
            "error": "Database operation failed"
        }), 503


@app.get("/stress")
def stress():
    if os.getenv("ENABLE_LOAD_TEST") != "true":
        return jsonify({"error": "Not found"}), 404

    try:
        iterations = int(
            request.args.get("iterations", "500000")
        )
    except ValueError:
        return jsonify({
            "error": "iterations must be an integer"
        }), 400

    if not 1 <= iterations <= 2_000_000:
        return jsonify({
            "error": "iterations must be between 1 and 2000000"
        }), 400

    value = 0
    for i in range(iterations):
        value = (value * 31 + i) % 1_000_000_007

    return jsonify({
        "status": "completed",
        "iterations": iterations,
        "result": value,
    }), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Internal server error"}), 500
