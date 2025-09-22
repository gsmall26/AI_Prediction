# scripts/view_predictions.py

import sqlite3
from tabulate import tabulate

DB_PATH = "data/predictions.db"

def view_recent_predictions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = """
    SELECT id, speaker_name, prediction_text, prediction_date, source_link
    FROM predictions
    ORDER BY id DESC
    LIMIT ?
    """
    rows = c.execute(query, (limit,)).fetchall()
    conn.close()

    if rows:
        headers = ["ID", "Speaker", "Text", "Date", "Link"]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    else:
        print("No predictions found.")

if __name__ == "__main__":
    view_recent_predictions(limit=10)
