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

import subprocess
import urllib.request

# from dotenv import load_dotenv
# load_dotenv()

from main_functions import query_wit, update_firestore, get_nutrition, query_firestore


app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

BOT_ID = '100302671815444'

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
                if recipient_id == BOT_ID:
                    return "Message Processed"
                if message['message'].get('text'):
                    user_msg = message['message']['text']
                    print("The user message that I'm passing in is this: " + user_msg)
                    process_response(recipient_id, user_msg)

                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    print(str(message))

                    if message['message']['attachments'][0]['type'] != 'audio':
                        bot.send_text_message(recipient_id, "I don't know how to understand that type of message, really sorry about that!")
                        return "Message Processed"
                    
                    try:
                        audio_url = message['message']['attachments'][0]['payload']['url']
                        urllib.request.urlretrieve(audio_url, "in.mp4")
                        command = "ffmpeg -y -i in.mp4 -ab 160k -ac 2 -ar 44100 -vn out.wav"
                        subprocess.call(command, shell=True)
                        print("success downloading file I think?")
                        process_response(recipient_id, 'out.wav', is_audio=True)
                        os.remove('out.wav')
                    except:
                        bot.send_text_message(recipient_id, "Looks like my ears are broken, oops! Try typing something instead.")

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#uses PyMessenger to send response to user
def process_response(recipient_id, user_msg, is_audio=False):
    #sends user the text message provided via input response parameter
    bot_response = get_response(user_msg, is_audio)
    bot.send_text_message(recipient_id, bot_response)
    return "success"

#chooses a random message to send to the user
def get_response(user_msg: str, is_audio) -> str:
    print()
    print("====")
    print("This is what I typed in: " + user_msg)
    print("====")
    print()


    resp = query_wit(msg=user_msg, is_audio=is_audio)
    
    # Doesn't match any intents
    if len(resp['intents']) == 0:
        return "That's not something I understand, sorry about that! :( (I'm trying to get smarter every day ;)"
    
    #TODO: process datetime entity
    elif resp['intents'][0]['name'] == 'foods_eaten_get':
        try:
            firestore_data = query_firestore(user_id="test", db=db, nutrition_type="foods_eaten")
            if firestore_data == -1:
                return "Looks like you don't exist yet in our systems! Try saying what you ate today and we'll get you registered up."
            elif firestore_data == -2:
                return "I don't think you've eaten anything today... Don't starve to death!"
            elif firestore_data == -3:
                return "I'm not really sure what information you're asking for. Are you sure that question is for me?"
            else:
                return "Here is what you've eaten today" + str(firestore_data)
        except:
            print("Error querying firestore")
            return "Beep boop, something went wrong. Looks like my internals are borked!"

    elif resp['intents'][0]['name'] == 'food_ate':
        # No food entity
        if 'food:food' not in resp['entities']:
            return "I'm not really sure what you ate... seems like I need to learn more about the world of humans!"
        food_ate = resp["entities"]['food:food'][0]['value']

        # Try to query Nutritionix
        try:
            food_nutrition = get_nutrition(food_ate)
        except:
            print("Error querying nutritionix! with parameter", food_ate)
            return "That food doesn't exist... does it?"
    
        # Try to update firestore
        try:
            update_firestore(user_id="test", db=db, food_nutrition=food_nutrition)
            return "Seems like you ate: " + str(food_ate) + ". Noted!"
        except:
            print("Error occured when updating firestore!")
            return "Beep boop, something went wrong. Looks like my internals are borked!"
        
    elif resp['intents'][0]['name'] == 'nutrition_query':
        # No nutrition_type entity
        if 'nutrition_type:nutrition_type' not in resp['entities']:
            return "I'm not really sure what information you're asking for. Are you sure that question is for me?"
        
        nutrition_type = resp["entities"]['nutrition_type:nutrition_type'][0]['value']
        
        try:
            firestore_data = query_firestore(user_id="test", db=db, nutrition_type=nutrition_type)
            if firestore_data == -1:
                return "Looks like you don't exist yet in our systems! Try saying what you ate today and we'll get you registered up."
            elif firestore_data == -2:
                return "I don't think you've eaten anything today... Don't starve to death!"
            elif firestore_data == -3:
                return "I'm not really sure what information you're asking for. Are you sure that question is for me?"
            else:
                return "Here is your " + str(nutrition_type) + " for today: " + str(firestore_data) + "."
        except:
            print("Error querying firestore")
            return "Beep boop, something went wrong. Looks like my internals are borked!"

    else:
        return "Bippity bop, looks like I'm borked!"



if __name__ == "__main__":
    app.run()