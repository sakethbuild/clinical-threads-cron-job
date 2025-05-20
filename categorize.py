from dotenv import load_dotenv
from pymongo import MongoClient
import os
import requests
from google import genai

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
        "{\"category\": <chosen_category_or_None>, \"confidence\": <confidence_score(between 0 and 1 eg 0.94)>} "
        "If the tweet does not fit any category, set category to null and confidence to a percentage. "
        "Do not return anything except the JSON."
    )
    client=genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(
    model='gemini-2.0-flash', contents=prompt
    )        
    # sample='''```json
    # {"category": "Critical Care", "confidence": 0.95}
    # ```'''
    return eval(response.text[7:-3].strip())
    #return eval(sample[7:-3].strip())

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