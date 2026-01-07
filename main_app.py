from flask import Flask, render_template, request, send_from_directory
import json
import os
from datetime import datetime
from Parser.Engine import app as Langapp

app = Flask(__name__)

LOG_FILE = os.path.join(app.root_path, "logs", "logs.json")

def save_log(entry: str):
    """Append log entry to logs.json"""
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry": entry
    })

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
# -----------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/main")
def login():
    return render_template("main.html")

@app.route("/lander")
def lander():
    return render_template("lander.html")

@app.route("/run", methods=["POST"])
def run():
    user_input = request.form["instruction"]

    # Run LangGraph
    result_state = Langapp.invoke({"input": user_input})
    output_text = result_state.get("result", "No result produced.")

    # Save output to logs
    if output_text:
        save_log(output_text)

    return render_template("main.html", output=output_text)
@app.route('/logs/logs.json')
def serve_logs_json():
    logs_dir = os.path.dirname(LOG_FILE)
    return send_from_directory(logs_dir, "logs.json")

@app.route("/logs")
def logs_page():
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    return render_template("logs.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True)
