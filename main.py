import os
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import time
from categorize import get_screen_ids,categorize
import json
import time
# Load environment variables from .env file
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

client = MongoClient(MONGODB_URI)
db = client['test'] 
tweets_collection = db['tweets']

def tweet_ids():
    tweet_ids=set()
    for t in tweets_collection.find():
        tweet_ids.add(t['tweet_id'])
    return tweet_ids

def fetch_last_20_tweets_for_all_users():
    ids = get_screen_ids()
    #ids = ['876254212371369985']
    for user_id in ids:
        url = f"https://twitter241.p.rapidapi.com/user-tweets?user={user_id}&count=5"
        headers = {
            "x-rapidapi-host": "twitter241.p.rapidapi.com",
            "x-rapidapi-key": os.getenv('RAPID_API_KEY')
        }
        response = requests.get(url, headers=headers)
        existing_tweet_ids = tweet_ids()
        if response.status_code == 200:
            data = response.json()['result']['timeline']['instructions'][-1]['entries']
            for d in data:
                if 'tweet-' in d['entryId']:
                    tweet_id = d['entryId'].replace('tweet-', '')
                    if tweet_id not in existing_tweet_ids:
                        tweet_data = d['content']['itemContent']['tweet_results']['result']
                        legacy = tweet_data['legacy']
                        tweet_text = legacy['full_text']
                        if tweet_text[:2]=='RT':
                            print('skippping cuz retweet')
                        else:
                            category_data = categorize(tweet_text)
                            # Prepare document
                            doc = {
                                "screen_name": tweet_data['core']['user_results']['result']['legacy']['screen_name'],
                                "tweet_id": tweet_id,
                                "tweet_text": tweet_text,
                                "created_at": legacy['created_at'],
                                "retweet_count": legacy.get('retweet_count', 0),
                                "favorite_count": legacy.get('favorite_count', 0),
                                "reply_count": legacy.get('reply_count', 0),
                                "tweet_url": f"https://twitter.com/{tweet_data['core']['user_results']['result']['legacy']['screen_name']}/status/{tweet_id}",
                                "category": category_data['category'],
                                "avatar_url": tweet_data['core']['user_results']['result']['legacy'].get('profile_image_url_https', ''),
                                "__v": 0,
                                "rest_id": user_id,
                                "flag": False,
                                "tagging_confidence": category_data['confidence'],
                            }
                            # Insert the tweet into MongoDB
                            tweets_collection.insert_one(doc)
                            print(f"Inserted tweet: {tweet_text} with ID: {tweet_id}")
                    else:
                        print('tweet already exists')
                time.sleep(5)
        else:
            print(f"Failed to fetch tweets for user {user_id}: {response.status_code}")
        time.sleep(5)
fetch_last_20_tweets_for_all_users()