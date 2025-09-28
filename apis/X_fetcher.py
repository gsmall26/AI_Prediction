import os
from dotenv import load_dotenv
import tweepy
import csv
import itertools
from utils.pipeline import process_and_insert
from utils.nlp import process_tweet_for_db

# Load API keys
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# Minimum thresholds
MIN_FOLLOWERS = 100
MIN_LIKES = 5
MIN_RETWEETS = 2
MIN_REPLIES = 0

# Load target users
def load_users(filepath="data/target_users.csv"):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Load keywords
def load_keywords(filepath="data/keywords.csv"):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Build query
def build_query(users, keywords):
    users_query = " OR ".join([f"from:{u}" for u in users])
    keywords_query = " OR ".join(keywords)
    return f"({users_query}) ({keywords_query})"

# Batching helper
def batch_list(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

# Fetch tweets with batching + NLP + DB insertion
def fetch_tweets(max_results=10, user_batch_size=1, keyword_batch_size=1):
    users = load_users()
    keywords = load_keywords()
    tweets_data = []

    user_batches = list(batch_list(users, user_batch_size))
    keyword_batches = list(batch_list(keywords, keyword_batch_size))

    for u_batch, k_batch in itertools.product(user_batches, keyword_batches):
        query = build_query(u_batch, k_batch)
        try:
            response = client.search_recent_tweets(
                query=query,
                tweet_fields=["id", "text", "created_at", "author_id", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username", "public_metrics", "verified"],
                max_results=max_results
            )

            if response.data:
                user_dict = {u.id: u for u in response.includes['users']}
                for tweet in response.data:
                    user = user_dict.get(tweet.author_id)
                    if not user:
                        continue

                    # Optional filtering
                    if (
                        user.public_metrics['followers_count'] < MIN_FOLLOWERS or
                        tweet.public_metrics.get("like_count", 0) < MIN_LIKES or
                        tweet.public_metrics.get("retweet_count", 0) < MIN_RETWEETS or
                        tweet.public_metrics.get("reply_count", 0) < MIN_REPLIES
                    ):
                        continue

                    tweet_dict = {
                        "author_username": user.username,
                        "author_id": tweet.author_id,
                        "followers_count": user.public_metrics['followers_count'],
                        "verified": user.verified,
                        "tweet_id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "reply_count": tweet.public_metrics.get("reply_count", 0),
                        "quote_count": tweet.public_metrics.get("quote_count", 0),
                        "tweet_link": f"https://twitter.com/{user.username}/status/{tweet.id}"
                    }

                    tweets_data.append(tweet_dict)

                    # --- NLP + DB insertion ---
                    # db_entry = process_and_insert(tweet_dict)
                    if tweet_dict is not None:
                        print("NLP processed result:")
                        db_entry = process_and_insert(tweet_dict)
                    else:
                        print(f"Skipped tweet by @{user.username}: invalid tweet data")


                    # Print the NLP-processed result
                    print("NLP processed result:")
                    for k, v in db_entry.items():
                        print(f"  {k}: {v}")
                    print("-" * 40)

        except Exception as e:
            print(f"Error fetching tweets for batch {u_batch} + {k_batch}: {e}")

    return tweets_data

if __name__ == "__main__":
    # For testing, use first user + first keyword to limit query
    users = load_users()
    keywords = load_keywords()
    test_user_batch = users[:1]
    test_keyword_batch = keywords[:1]

    tweets = fetch_tweets(
        max_results=10,
        user_batch_size=len(test_user_batch),
        keyword_batch_size=len(test_keyword_batch)
    )

    print(f"Fetched {len(tweets)} tweets.")
    for t in tweets:
        print(t)
