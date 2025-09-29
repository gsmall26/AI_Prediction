import sqlite3
from utils.nlp import process_tweet_for_db

DB_PATH = "data/predictions.db"


def insert_entry(db_entry, db_path=DB_PATH):
    # insert a record into predictions table
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    columns = ", ".join(db_entry.keys())
    placeholders = ", ".join("?" for _ in db_entry)
    sql = f"INSERT INTO predictions ({columns}) VALUES ({placeholders})"
    c.execute(sql, tuple(db_entry.values()))
    conn.commit()
    conn.close()


def process_entry(raw_item):
    # run NLP and return a cleaned dict ready for DB
    return process_tweet_for_db(raw_item)


def process_and_insert(raw_item, db_path=DB_PATH):
    # process a raw item and insert it into DB
    entry = process_entry(raw_item)
    insert_entry(entry, db_path)
    print(f"Inserted by @{entry['speaker_name']} into DB")
    return entry
