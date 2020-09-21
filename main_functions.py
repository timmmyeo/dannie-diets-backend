import requests
import json

# from dotenv import load_dotenv
# load_dotenv()

import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime

from wit import Wit



# Retrieves essential information from the nutrionix API given a query
def get_nutrition(query):
  API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
  
  HEADERS = {
  "Content-Type": "application/json",
  "x-app-id": os.environ['NUTRIONIX_APP_ID'],
  "x-app-key": os.environ['NUTRITONIX_APP_KEY']
  }

  BODY = {
  "query": query
  }

  r = requests.post(url = API_URL, headers=HEADERS, data=json.dumps(BODY)) 

  data = r.json() 

  return {
    "food_name": data['foods'][0]["food_name"],
    "calories": data['foods'][0]["nf_calories"],
    "fat_g": data['foods'][0]["nf_total_fat"],
    "sodium_mg": data['foods'][0]["nf_sodium"],
    "protein_g": data['foods'][0]["nf_protein"]
    }

# # Updates the firestore given the user, food they ate, and nutritional information about that food
def update_firestore(user_id, db, food_nutrition):

  current_date = datetime.today().strftime('%d-%m-%Y') 

  user_doc= db.collection('users').document(user_id)
  user_doc.update({
      current_date: {
        "food": firestore.ArrayUnion([food_nutrition['food_name']]),
        "total_nutrition": {
          "calories": firestore.Increment(food_nutrition['calories']),
          "fat_g": firestore.Increment(food_nutrition['fat_g']),
          "sodium_mg": firestore.Increment(food_nutrition['sodium_mg']),
          "protein_g": firestore.Increment(food_nutrition['protein_g'])
        }
      }
  })

# Queries Wit.ai and returns useful information 
# TODO: if confidence is below 50%, then maybe return None?
def query_wit(msg):
  print("Querying wit with " + msg)
  client = Wit(os.environ['WIT_KEY'])
  resp = client.message(msg)
  print('Yay, got Wit.ai response: ' + str(resp))
  return resp

if __name__ == "__main__":
    # update_firestore("test", "banana")
    # get_nutrition("bottle")
    # query_wit("I had a cake just now")
    pass

