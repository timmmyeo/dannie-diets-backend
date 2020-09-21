#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import base64

# from dotenv import load_dotenv
# load_dotenv()

from main_functions import query_wit, update_firestore, get_nutrition


app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

GOOGLE_FIREBASE_KEY = str.encode(os.environ['GOOGLE_FIREBASE_KEY'])
cred = credentials.Certificate(json.loads(base64.decodebytes(GOOGLE_FIREBASE_KEY)))
firebase_admin.initialize_app(cred)

db = firestore.client()

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
    #    print()
    #    print("*********")
    #    print("json of request:")
    #    print(str(output))
    #    print("**********")
    #    print()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                # We don't want to process the bot response!
                if recipient_id == '100302671815444':
                    return "Message Processed"
                if message['message'].get('text'):
                    user_msg = message['message']['text']
                    print("The user message that I'm passing in is this: " + user_msg)
                    process_response(recipient_id, user_msg)

                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    # send_message(recipient_id, str(message))
                    # send_message(recipient_id, message['message']["attachments"][0]["type"])
                    # send_message(recipient_id, message['message']["attachments"][0]["payload"]["url"])
                    # response_sent_nontext = get_message()
                    # send_message(recipient_id, response_sent_nontext)
                    pass
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#uses PyMessenger to send response to user
def process_response(recipient_id, user_msg):
    #sends user the text message provided via input response parameter
    bot_response = get_response(user_msg)
    bot.send_text_message(recipient_id, bot_response)
    return "success"

#chooses a random message to send to the user
def get_response(user_msg: str) -> str:
    print()
    print("====")
    print("This is what I typed in: " + user_msg)
    print("====")
    print()
    resp = query_wit(user_msg)
    
    # Doesn't match any intents
    if len(resp['intents']) == 0:
        return "That's not something I understand, sorry about that! :( (I'm trying to get smarter every day ;)"

    elif resp['intents'][0]['name'] == 'food_ate':
        # No food entity
        if 'food:food' not in resp['entities']:
            return "I'm not really sure what you ate... seems like I need to learn more about the world of humans!"
        food_ate = resp["entities"]['food:food'][0]['value']

        # Try to query Nutrionix
        try:
            food_nutrition = get_nutrition(food_ate)
        except:
            print("Error querying nutrionix! with parameter", food_ate)
            return "That food doesn't exist... does it?"
    
        # Try to update firestore
        try:
            update_firestore(user_id="test", db=db, food_nutrition=food_nutrition)
            return "Seems like you ate: " + str(food_ate) + ". Noted!"
        except:
            print("Error occured when updating firestore!")
            return "That food doesn't exist... does it?"
        
    elif resp['intents'][0]['name'] == 'nutrition_query':
        return "So you're interested in your health, great!"
    else:
        return "Bippity bop, looks like I'm borked!"



if __name__ == "__main__":
    app.run()