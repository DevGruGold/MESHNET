
from flask import Flask, request, jsonify
from git import Repo
import os, json, time

app = Flask(__name__)

GITHUB_USERNAME = "DevGruGold"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set as environment variable
REPO_NAME = "MESHNET"
CLONE_DIR = "/tmp/meshnet_repo"
SCOREBOARD_FILE = "meshnet_scoreboard.json"

def clone_repo():
    if os.path.exists(CLONE_DIR):
        os.system(f"rm -rf {CLONE_DIR}")
    url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    return Repo.clone_from(url, CLONE_DIR)

@app.route("/submit", methods=["POST"])
def update_scoreboard():
    data = request.get_json()
    if not all(k in data for k in ("node_id", "hashrate", "timestamp")):
        return jsonify({"error": "Missing fields"}), 400

    repo = clone_repo()
    filepath = os.path.join(CLONE_DIR, SCOREBOARD_FILE)

    if os.path.exists(filepath):
        with open(filepath) as f:
            scoreboard = json.load(f)
    else:
        scoreboard = []

    found = False
    for entry in scoreboard:
        if entry["node_id"] == data["node_id"]:
            entry.update({
                "hashrate": data["hashrate"],
                "timestamp": data["timestamp"]
            })
            found = True
            break
    if not found:
        scoreboard.append(data)

    with open(filepath, "w") as f:
        json.dump(scoreboard, f, indent=2)

    repo.git.add(SCOREBOARD_FILE)
    repo.index.commit(f"Update from {data['node_id']} at {data['timestamp']}")
    repo.remote(name="origin").push()

    return jsonify({"status": "success", "updated": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
