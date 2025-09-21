import os
from dotenv import load_dotenv
import tweepy
import csv
import itertools

# Load API keys from .env
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate with OAuth2 (Bearer Token)
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# Minimum thresholds
MIN_FOLLOWERS = 100        # Only fetch tweets from users with >= 100 followers
MIN_LIKES = 5
MIN_RETWEETS = 2
MIN_REPLIES = 0

# Load target users from CSV
def load_users(filepath="data/target_users.csv"):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Load keywords from CSV
def load_keywords(filepath="data/keywords.csv"):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Build the search query for Twitter API
def build_query(users, keywords):
    users_query = " OR ".join([f"from:{u}" for u in users])
    keywords_query = " OR ".join(keywords)
    return f"({users_query}) ({keywords_query})"

def batch_list(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

# Updated fetch_tweets with batching
def fetch_tweets(max_results=10, user_batch_size=1, keyword_batch_size=1):
    users = load_users()
    keywords = load_keywords()
    
    tweets_data = []

    # Generate batches
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
                    # if not user or user.public_metrics['followers_count'] < MIN_FOLLOWERS:
                    #     continue
                    # if (
                    #     tweet.public_metrics.get("like_count", 0) < MIN_LIKES or
                    #     tweet.public_metrics.get("retweet_count", 0) < MIN_RETWEETS or
                    #     tweet.public_metrics.get("reply_count", 0) < MIN_REPLIES
                    # ):
                    #     continue
                    tweets_data.append({
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
                    })
        except Exception as e:
            print(f"Error fetching tweets for batch {u_batch} + {k_batch}: {e}")

    return tweets_data

if __name__ == "__main__":
    # For testing, just take first user and first keyword to generate one query
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


# if __name__ == "__main__":
#     tweets = fetch_tweets()
#     print(f"Fetched {len(tweets)} tweets.")
#     for t in tweets:  # can slice tweets[:5] to show first 5
#         print(t)
