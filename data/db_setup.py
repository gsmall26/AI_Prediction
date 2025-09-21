import sqlite3

conn = sqlite3.connect("data/predictions.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    speaker_name TEXT,
    organization TEXT,
    prediction_text TEXT,
    subject_topic TEXT,
    prediction_type TEXT,
    prediction_category TEXT,
    timeframe_as_stated TEXT,
    timeframe_start DATE,
    timeframe_end DATE,
    certainty_level TEXT,
    conditional BOOLEAN,
    prediction_date DATE,
    source_type TEXT,
    source_link TEXT,
    resolution_date DATE,
    outcome TEXT,
    outcome_evidence TEXT,
    scoring_confidence REAL,
    tags_keywords TEXT,
    notes TEXT
)
""")

conn.commit()
conn.close()
print("Database and predictions table created successfully.")
