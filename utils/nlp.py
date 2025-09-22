import re
from datetime import datetime
import spacy

# Load spaCy model (small English model)
nlp_model = spacy.load("en_core_web_sm")


"""
This module processes a post and prepares it for database insertion.

process_tweet_for_db expectes dictionary structure for nlp
tweet_dict = {
    "text": "The content of the post",
    "author_username": "user123",
    "created_at": datetime.utcnow(),
    "tweet_link": "https://...",
    "author_id": 12345,  # optional
    "followers_count": 1000,  # optional
    "verified": True  # optional
}
"""

def process_tweet_for_db(tweet_dict):
    """
    Convert a raw tweet dictionary into a dictionary ready for SQLite insertion
    matching the predictions table schema.

    Args:
        tweet_dict (dict): Raw tweet data from X_fetcher.py

    Returns:
        dict: DB-ready dictionary with all keys from predictions table
    """
    text = tweet_dict.get("text", "")
    cleaned_text = clean_text(text)

    # NLP extractions
    subject_topic = extract_topic(cleaned_text)
    timeframe_as_stated, timeframe_start, timeframe_end = extract_timeframe(cleaned_text)
    conditional = detect_conditional(cleaned_text)
    certainty_level = extract_certainty(cleaned_text)
    tags_keywords = extract_keywords(cleaned_text)

    db_entry = {
        "speaker_name": tweet_dict.get("author_username", ""),
        "organization": None,
        "prediction_text": cleaned_text,
        "subject_topic": subject_topic,
        "prediction_type": "prediction" if conditional else "statement",
        "prediction_category": None,
        "timeframe_as_stated": timeframe_as_stated,
        "timeframe_start": timeframe_start,
        "timeframe_end": timeframe_end,
        "certainty_level": certainty_level,
        "conditional": conditional,
        "prediction_date": tweet_dict.get("created_at", datetime.utcnow()),
        "source_type": "Twitter",
        "source_link": tweet_dict.get("tweet_link", ""),
        "resolution_date": None,
        "outcome": None,
        "outcome_evidence": None,
        "scoring_confidence": None,
        "tags_keywords": tags_keywords,
        "notes": None
    }

    return db_entry


def clean_text(text):
    """
    Clean tweet text: remove URLs, mentions, hashtags, emojis, non-ASCII characters,
    and normalize whitespace.
    """
    text = re.sub(r"http\S+|@\S+|#\S+", "", text)  # remove URLs, mentions, hashtags
    text = re.sub(r"[^\x00-\x7F]+", "", text)      # remove non-ASCII characters
    text = re.sub(r"\s+", " ", text).strip()      # collapse whitespace
    return text


def extract_topic(text):
    """
    Extract a subject/topic from text using spaCy noun chunks.
    """
    doc = nlp_model(text)
    nouns = [chunk.text for chunk in doc.noun_chunks]
    if nouns:
        return nouns[0]  # first noun phrase
    return None


def extract_timeframe(text):
    """
    Naively extract timeframe from text. Returns:
        timeframe_as_stated (str), timeframe_start (YYYY-MM-DD), timeframe_end (YYYY-MM-DD)
    """
    # Regex for year (e.g., 2025)
    match = re.search(r"\b(20\d{2})\b", text)
    if match:
        year = match.group(1)
        return year, f"{year}-01-01", f"{year}-12-31"
    return None, None, None


def detect_conditional(text):
    """
    Detects if the text contains a conditional statement (if...then...).
    """
    return bool(re.search(r"\bif\b.*\bthen\b", text, re.IGNORECASE))


def extract_certainty(text):
    """
    Determine certainty level: high, medium, low, or None.
    """
    text = text.lower()
    if any(w in text for w in ["likely", "certain", "definitely", "will"]):
        return "high"
    elif any(w in text for w in ["may", "might", "possible", "could"]):
        return "medium"
    elif any(w in text for w in ["uncertain", "unknown", "doubt"]):
        return "low"
    return None


def extract_keywords(text):
    """
    Extract keywords from text using named entities and nouns.
    Returns up to 10 unique keywords as comma-separated string.
    """
    doc = nlp_model(text)
    keywords = [ent.text for ent in doc.ents] + [token.lemma_ for token in doc if token.pos_ in ("NOUN", "PROPN")]
    # Remove duplicates while preserving order
    unique_keywords = list(dict.fromkeys(keywords))
    return ",".join(unique_keywords[:10])
