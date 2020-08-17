import os
import neispy
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
            text = message['message'].get('text')
            response_sent_text = choice_message(text)
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


def choice_message(text=""):
  selections = {
    '급식': get_meal(date=20200804),
    '학사일정': get_schedule(date=20200804),
    '시간표': get_timetable(date=20200804),
    'notselected': ''
  }

  result = 'notselected'

  for i in selections:
    if i in text:
      result = i

  try:
    return selections[result]
  except Exception as err:
    print(err)
    return '몰랑~'


def send_message(recipient_id, response):
  bot.send_text_message(recipient_id, response)
  return "success"

def get_meal(date=None):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  try:
    if date:
      meal_info = neis.mealServiceDietInfo(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, MLSV_YMD=date)
    else:
      meal_info = neis.mealServiceDietInfo(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE)

    meal = meal_info.DDISH_NM.replace('<br/>', '\n')
    return meal
  except Exception as err:
    print(err)
    return "해당 날짜의 급식정보가 없습니다"

def get_schedule(date=None):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  try:
    if date:
      schedule_info = neis.SchoolSchedule(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, MLSV_YMD=date)
    else:
      schedule_info = neis.SchoolSchedule(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE)

    schedule = schedule_info.EVENT_NM

    return schedule
  except Exception as err:
    print(err)
    return "해당 날짜의 학사일정 정보가 없습니다"

def get_timetable(date=None, grade_no=1, class_no=1):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  try:
    if date:
      timetable_info = neis.timeTable(schclass='his', ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, ALL_TI_YMD=date, GRADE=grade_no, CLASS_NM=class_no)
    else:
      timetable_info = neis.timeTable(schclass='his', ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, GRADE=grade_no, CLASS_NM=class_no)

    timetable = [i['ITRT_CNTNT'] for i in timetable_info.data]
    return timetable
  except Exception as err:
    print(err)
    return "해당 날짜의 시간표 정보가 없습니다"

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)