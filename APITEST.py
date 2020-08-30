from flask import Flask
import requests
import json
import config
app = Flask(__name__)

app.config.from_object("config.Config")

@app.route('/')
def hello_world():
  # api-endpoint 
  URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

  HEADERS = {
    "Content-Type": "application/json",
    "x-app-id": app.config["NUTRIONIX_APP_ID"],
    "x-app-key": app.config["NUTRITONIX_APP_KEY"]
  }

  BODY = {
 "query":"mcdonald's burger"
}
    
  # sending get request and saving the response as response object 
  r = requests.post(url = URL, headers=HEADERS, data=json.dumps(BODY)) 
    
  # extracting data in json format 
  data = r.json() 

  return data