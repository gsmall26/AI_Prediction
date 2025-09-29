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
        conn.row_factory = sqlite3.Row  # allows accessing columns by name
        c = conn.cursor()
        c.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()

        # Map DB column names to friendly names
        friendly_keys = {
            "id": "id",
            "speaker_name": "speaker",
            "organization": "organization",
            "prediction_text": "text",
            "subject_topic": "topic",
            "prediction_type": "type",
            "prediction_category": "category",
            "timeframe_as_stated": "timeframe_as_stated",
            "timeframe_start": "timeframe_start",
            "timeframe_end": "timeframe_end",
            "certainty_level": "certainty_level",
            "conditional": "conditional",
            "prediction_date": "date",
            "source_type": "source_type",
            "source_link": "link",
            "resolution_date": "resolution_date",
            "outcome": "outcome",
            "outcome_evidence": "outcome_evidence",
            "scoring_confidence": "scoring_confidence",
            "tags_keywords": "keywords",
            "notes": "notes"
        }

        # Define a preferred order for JSON output
        preferred_order = [
            "id", "speaker", "organization", "text", "topic", "type", "category",
            "date", "timeframe_as_stated", "timeframe_start", "timeframe_end",
            "certainty_level", "conditional", "source_type", "link",
            "resolution_date", "outcome", "outcome_evidence",
            "scoring_confidence", "keywords", "notes"
        ]

        predictions_list = []
        for row in rows:
            row_dict = {friendly_keys.get(k, k): row[k] if row[k] is not None else None for k in row.keys()}
            # Reorder according to preferred_order
            ordered_row = {k: row_dict.get(k) for k in preferred_order}
            predictions_list.append(ordered_row)

        return jsonify(predictions_list)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




# Run Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
