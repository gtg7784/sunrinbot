import os
import neispy
from datetime import datetime
from flask import Flask, request
from dotenv import load_dotenv
from pymessenger.bot import Bot

load_dotenv(verbose=True)

app = Flask(__name__)

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)

SCHOOL_NAME = "선린인터넷고등학교"

@app.route('/', methods=['GET', 'POST'])
def chat():
  if request.method == 'GET':
    token_sent = request.args.get('hub.verify_token')
    return vertify_token(token_sent)
  else:
    output = request.get_json()
    for event in output['entry']:
      messaging = event['messaging']
      for message in messaging:
        if message.get('message'):
          recipient_id = message['sender']['id']
          if message['message'].get('text'):
            response_sent_text = get_meal()
            send_message(recipient_id, response_sent_text)
          if message['message'].get('attachments'):
            response_sent_nontext = "attach"
            send_message(recipient_id, response_sent_nontext)
  return "Message Processed"

@app.route('/test', methods=['GET'])
def test():
  return "HELLO WORLD"

def vertify_token(token):
  if token == VERIFY_TOKEN:
    return request.args.get('hub.challenge')
  return 'Invalid Verification Token'


def choice_message(text):
  selections = ['급식', ]

def send_message(recipient_id, response):
  bot.send_text_message(recipient_id, response)
  return "success"

def get_meal():
  API_TOKEN = os.getenv('OPEN_API_TOKEN')
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  date = datetime.now().strftime('%Y%m%d')

  try:
    meal_info = neis.mealServiceDietInfo(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, MLSV_YMD=20200804)
    print(meal_info)
    return meal_info
  except Exception as error:
    print(error)
    return "해당 날짜의 급식정보가 없습니다"


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)