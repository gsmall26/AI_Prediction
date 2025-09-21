from utils import nlp
from apis import X_fetcher
import sqlite3
from datetime import datetime

tweets = X_fetcher.fetch_tweets(max_results=10)  # or whatever batch you want

processed_tweets = []
for tweet in tweets:
    db_ready = nlp.process_tweet_for_db(tweet)
    processed_tweets.append(db_ready)


conn = sqlite3.connect("data/predictions.db")
cursor = conn.cursor()

for tweet in processed_tweets:
    cursor.execute("""
        INSERT INTO predictions (
            speaker_name, organization, prediction_text, subject_topic,
            prediction_type, prediction_category, timeframe_as_stated,
            timeframe_start, timeframe_end, certainty_level, conditional,
            prediction_date, source_type, source_link, resolution_date,
            outcome, outcome_evidence, scoring_confidence, tags_keywords, notes
        ) VALUES (
            :speaker_name, :organization, :prediction_text, :subject_topic,
            :prediction_type, :prediction_category, :timeframe_as_stated,
            :timeframe_start, :timeframe_end, :certainty_level, :conditional,
            :prediction_date, :source_type, :source_link, :resolution_date,
            :outcome, :outcome_evidence, :scoring_confidence, :tags_keywords, :notes
        )
    """, tweet)

conn.commit()
conn.close()
