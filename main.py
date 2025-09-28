from flask import Flask, jsonify, request, render_template
from apis.X_fetcher import fetch_tweets
from utils.pipeline import process_and_insert
import sqlite3

app = Flask(__name__)

DB_PATH = "data/predictions.db"


@app.route("/")
def home():
    return """
    <h1>AI Prediction Tracking System</h1>
    <p>Endpoints available:</p>
    <ul>
        <li>/fetch - Fetch tweets and process predictions</li>
        <li>/predictions - View current predictions in database</li>
    </ul>
    """

# Fetch tweets route
@app.route("/fetch", methods=["GET"])
def fetch():
    try:
        tweets = fetch_tweets(max_results=10)
        return jsonify({
            "status": "success",
            "tweets_processed": len(tweets)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# View predictions route
@app.route("/predictions", methods=["GET"])
def predictions():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT speaker_name, prediction_text, prediction_date, source_link FROM predictions ORDER BY id DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()

        predictions_list = [
            {
                "speaker": row[0],
                "text": row[1],
                "date": row[2],
                "link": row[3]
            } for row in rows
        ]

        return jsonify(predictions_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Run Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
