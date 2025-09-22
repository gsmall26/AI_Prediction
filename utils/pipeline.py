import sqlite3
from utils.nlp import process_tweet_for_db

DB_PATH = "data/predictions.db"

def insert_prediction(db_entry, db_path=DB_PATH):
    #insert cleaned up data into predictions table

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    columns = ", ".join(db_entry.keys())
    placeholders = ", ".join("?" for _ in db_entry)
    sql = f"INSERT INTO predictions ({columns}) VALUES ({placeholders})"
    c.execute(sql, tuple(db_entry.values()))
    conn.commit()
    conn.close()

def process_and_insert(tweet_dict, db_path=DB_PATH):
    #run the NLP processing on dictionary structure, call insertion function
    
    db_entry = process_tweet_for_db(tweet_dict)
    insert_prediction(db_entry)
    print(f"Inserted tweet by @{db_entry['speaker_name']} into DB")

