import api_secrets

from datetime import datetime

import os
import redis
import time
import traceback
import tweepy

# With the following settings, the program will fetch between 75k and 491k tweets per month
# This is below the total rate limits for the API if you don't use the same tokens somewhere else.
DEFAULT_MAX_RESULTS = int(os.environ['DEFAULT_MAX_RESULTS']) # How many tweets are we tracking
RECENT_TWEET_THRESHOLD = int(os.environ['RECENT_TWEET_THRESHOLD']) # Max age (seconds) for a tweet to count as recent
REFRESH_RATE_IF_RECENT_TWEETS = int(os.environ['REFRESH_RATE_IF_RECENT_TWEETS']) # Track every x seconds if there is a recent tweet
REFRESH_RATE_DEFAULT = int(os.environ['REFRESH_RATE_DEFAULT']) # Track every x seconds if no recent tweet
WATCH_REFRESH_RATE = int(os.environ['WATCH_REFRESH_RATE']) # Watch for new tweets every x seconds

FIELDS_ORDER = ['impression_count', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'user_profile_clicks', 'url_link_clicks']
USER_ID = api_secrets.USER_ACCESS_TOKEN.split('-')[0]

redis_cli = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=0)

tweepy_client = tweepy.Client(bearer_token=api_secrets.BEARER_TOKEN,
                       consumer_key=api_secrets.API_KEY,
                       consumer_secret=api_secrets.API_KEY_SECRET,
                       access_token=api_secrets.USER_ACCESS_TOKEN,
                       access_token_secret=api_secrets.USER_ACCESS_TOKEN_SECRET)

def fetch_tweet_metrics(max_results=DEFAULT_MAX_RESULTS):
    query = tweepy_client.get_users_tweets(USER_ID, user_auth=True, max_results=max_results, tweet_fields=['created_at', 'public_metrics', 'non_public_metrics'])
    timestamp = int(time.time())
    min_tweet_age = float('inf')
    for tweet in query.data:
        metrics = tweet.public_metrics
        metrics.update(tweet.non_public_metrics)
        metrics_vector = [metrics.get(field, -1) for field in FIELDS_ORDER]
        redis_cli.hset(str(tweet.id), str(timestamp), str(metrics_vector).replace(' ',''))
        creation_timestamp = int(datetime.timestamp(tweet.created_at))
        redis_cli.hsetnx('creation_date', str(tweet.id), str(creation_timestamp))
        redis_cli.hsetnx('tweet_text', str(tweet.id), tweet.text)
        min_tweet_age = min(min_tweet_age, timestamp - creation_timestamp)
    myself = tweepy_client.get_user(id=USER_ID, user_fields='public_metrics')
    nb_followers = myself.data.public_metrics['followers_count']
    redis_cli.hsetnx('followers', str(timestamp), nb_followers)
    return len(query.data), min_tweet_age

def get_metrics_history(tweet_id):
    return redis_cli.hgetall(tweet_id)

if __name__ == '__main__':
    last_fetch_timestamp = 0
    while True:
        try:
            n_results, min_tweet_age = fetch_tweet_metrics(max_results=5)
            time_since_fetch = int(time.time()) - last_fetch_timestamp
            print(f'[{time.ctime()}] Watch loop: got {n_results} tweets. Most recent is {min_tweet_age // 60} minutes old. Last fetch was {time_since_fetch // 60} minutes ago.')
            if min_tweet_age <= RECENT_TWEET_THRESHOLD and time_since_fetch >= REFRESH_RATE_IF_RECENT_TWEETS:
                print('Found recent tweets, triggering fast fetch.')
                n_results, min_tweet_age = fetch_tweet_metrics()
                print(f'Fast fetch cycle done, got {n_results} tweets.')
                last_fetch_timestamp = int(time.time())
            elif time_since_fetch >= REFRESH_RATE_DEFAULT:
                print('Triggering slow fetch.')
                n_results, min_tweet_age = fetch_tweet_metrics()
                print(f'Slow fetch cycle done, got {n_results} tweets.')
                last_fetch_timestamp = int(time.time())
            time.sleep(WATCH_REFRESH_RATE)
        except Exception as e:
            print('Encountered error while fetching stats:')
            traceback.print_exc()
            time.sleep(WATCH_REFRESH_RATE)
