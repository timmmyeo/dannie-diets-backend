import requests
import json
from dotenv import load_dotenv
load_dotenv()

import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime


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

  print(data)

  return {
    "food_name": data['foods'][0]["food_name"],
    "calories": data['foods'][0]["nf_calories"],
    "fat_g": data['foods'][0]["nf_total_fat"],
    "sodium_mg": data['foods'][0]["nf_sodium"],
    "protein_g": data['foods'][0]["nf_protein"]
    }

# Updates the firestore given the user, food they ate, and nutritional information about that food
def update_firestore(user_id, food, calories, fat_g, sodium_mg, protein_g):
  cred = credentials.Certificate('./serviceAccountKey.json')
  firebase_admin.initialize_app(cred)

  db = firestore.client()

  current_date = datetime.today().strftime('%d-%m-%Y') 

  user_doc= db.collection('users').document(user_id)
  user_doc.update({
      current_date: {
        "food": firestore.ArrayUnion([food]),
        "total_nutrition": {
          "calories": firestore.Increment(calories),
          "fat_g": firestore.Increment(fat_g),
          "sodium_mg": firestore.Increment(sodium_mg),
          "protein_g": firestore.Increment(protein_g)
        }
      }
  })


if __name__ == "__main__":
    # update_firestore("test", "banana", 100, 10, 10, 10)
    # get_nutrition("bottle")