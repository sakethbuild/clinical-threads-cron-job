import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['test']
tweets_collection = db['tweets']

c = 0
for tweet in tweets_collection.find():
    if tweet['tweet_text'][0:2] == 'RT':
        tweets_collection.delete_one({'_id': tweet['_id']})
        print(f"Removed tweet with id: {tweet['_id']} and text: {tweet['tweet_text']}")
        c += 1
print(f"Total removed: {c}")
