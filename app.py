import logging
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

# Enable logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["webhookDB"]
collection = db["events"]

# Format timestamp nicely
def format_time(iso_str):
    try:
        if iso_str.endswith('Z'):
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        else:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        dt = datetime.utcnow()
    return dt.strftime("%-d %B %Y - %-I:%M %p UTC")

# GitHub webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    message = None
    timestamp = None

    if event_type == "push":
        author = data["pusher"]["name"]
        branch = data["ref"].split("/")[-1]
        timestamp = data["head_commit"]["timestamp"]
        message = f"{author} pushed to {branch} on {format_time(timestamp)}"

    elif event_type == "pull_request":
        action = data["action"]
        if action not in ["opened", "closed"]:
            logging.info(f"Ignored PR action: {action}")
            return "", 204

        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        timestamp = data["pull_request"]["created_at"]

        if action == "closed" and data["pull_request"].get("merged"):
            message = f"{author} merged branch {from_branch} to {to_branch} on {format_time(timestamp)}"
        else:
            message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {format_time(timestamp)}"

    if message:
        logging.info(f"Received {event_type}: {message}")
        collection.insert_one({"message": message, "timestamp": timestamp})
        return "OK", 200

    logging.warning(f"Unhandled event type: {event_type}")
    return "", 204

# Fetch events
@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(20))
    return jsonify([{"message": e["message"], "timestamp": e["timestamp"]} for e in events])

@app.route('/')
def index():
    return render_template('events.html')

if __name__ == '__main__':
    app.run(debug=True)
