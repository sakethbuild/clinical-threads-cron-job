from dotenv import load_dotenv
from pymongo import MongoClient
import os
import requests
import google.generativeai as genai

load_dotenv()

def get_categories():
    MONGODB_URI = os.getenv('MONGODB_URI')
    RAPID_API_KEY = os.getenv('RAPID_API_KEY')
    client = MongoClient(MONGODB_URI)
    db = client['test'] 
    categories = db['categories']
    return [x['category_name'] for x in categories.find()]


def categorize(tweet_text):
    categories = get_categories()
    
    prompt = (
        f"Given the following tweet:\n\"{tweet_text}\"\n\n"
        f"And these categories: {categories}\n\n"
        "Classify the tweet into one of the categories. "
        "Respond strictly in JSON format as: "
        "{\"category\": <chosen_category_or_null>, \"confidence\": <confidence_score (between 0 and 1, e.g., 0.94)>} "
        "If the tweet does not fit any category, set category to null. "
        "Do not return anything except the JSON."
    )

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    try:
        import json
        return json.loads(response.text.strip().strip("```json").strip("```").strip())
    except Exception as e:
        print("Error parsing response:", response.text)
        raise e

def get_screen_ids():
    MONGODB_URI = os.getenv('MONGODB_URI')
    RAPID_API_KEY = os.getenv('RAPID_API_KEY')
    client = MongoClient(MONGODB_URI)
    db = client['test'] 
    tweets=db['tweets']    
    ids=set()
    for t in tweets.find():
        ids.add(t['rest_id'])
    return ids

#print(categorize("https://twitter.com/ross_prager/status/1861094690528891344"))
    
#print(get_screen_ids())
#print(get_categories())
