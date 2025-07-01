from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# Connect to local MongoDB (we'll change this to online later)
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)

db = client["webhookDB"]
events = db["events"]

@app.route("/webhook", methods=["POST"])
def github_webhook():
    data = request.json
    event = request.headers.get("X-GitHub-Event")
    payload = {}

    if event == "push":
        payload = {
            "type": "push",
            "author": data["pusher"]["name"],
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.now()
        }

    elif event == "pull_request":
        pr = data["pull_request"]
        payload = {
            "type": "merge" if pr["merged_at"] else "pull_request",
            "author": pr["user"]["login"],
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.now()
        }

    events.insert_one(payload)
    return "OK", 200

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/get-events", methods=["GET"])
def get_events():
    data = list(events.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))
    return jsonify(data=data)

if __name__ == "__main__":
    app.run(port=5000)
