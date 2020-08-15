import os
import random
from flask import Flask, request
from dotenv import load_dotenv
from pymessenger.bot import Bot

load_dotenv(verbose=True)
app = Flask(__name__)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)

@app.route('/', methods=['GET', 'POST'])
def chat():
  if request.method == 'GET':
    token_sent = request.args.get('hub.vertify_token')
    return vertify_token(token_sent)
  else:
    output = request.get_json()
    for event in output['entry']:
      messaging = event['messaging']
      for message in messaging:
        if message.get('message'):
          recipient_id = message['sender']['id']
          if message['message'].get('text'):
            response_sent_text = get_message()
            send_message(recipient_id, response_sent_text)
          if message['message'].get('attachments'):
            response_sent_nontext = get_message()
            send_message(recipient_id, response_sent_nontext)


@app.route('/test', methods=['GET'])
def test():
  return "HELLO WORLD"

def vertify_token(token):
  if token == VERIFY_TOKEN:
    return request.args.get('hub.chellenge')
  return 'Invalid Verification Token'

def get_message():
  sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
  return random.choice(sample_responses)

def send_message(recipient_id, response):
  bot.send_text_message(recipient_id, response)
  return "success"

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)