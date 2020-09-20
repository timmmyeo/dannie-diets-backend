import requests
import json
from dotenv import load_dotenv
load_dotenv()

import os


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

  def update_firebase():
    


if __name__ == "__main__":
    print(get_nutrition("hamburger"))