import nlp
import mock_tweets

if __name__ == "__main__":
    for i, tweet in enumerate(mock_tweets.mock_tweets, start=1):
        processed = nlp.process_tweet_for_db(tweet)
        print(f"Processed tweet {i}:")
        for k, v in processed.items():
            print(f"  {k}: {v}")
        print("-" * 40)
