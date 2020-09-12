import os
import argparse
import neispy
from datetime import datetime
from flask import Flask, request
from dotenv import load_dotenv
from pymessenger.bot import Bot
from model import KoGPT2Chat

load_dotenv(verbose=True)

parser = argparse.ArgumentParser(description='Ruby based on KoGPT-2')
parser.add_argument('--model_params', type=str, default='model_chp/model_last.ckpt')
args = parser.parse_args()

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
    '급식': get_meal(text),
    '학사일정': get_schedule(),
    '시간표': get_timetable(),
    '사용법': get_howtouse(),
  }

  print(text)

  result = ''

  for i in selections:
    if i in text:
      result = i

  try:
    return selections[result]
  except Exception as err:
    print(err)
    return chat_with_ai(text)


def send_message(recipient_id, response):
  bot.send_text_message(recipient_id, response)
  return "success"

def get_meal(text):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  try:
    YMD = get_ymd(text)
    if YMD:
      meal_info = neis.mealServiceDietInfo(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, MLSV_YMD=YMD)
    else:
      meal_info = neis.mealServiceDietInfo(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE)

    meal = meal_info.DDISH_NM.replace('<br/>', '\n')
    
    return meal
  except Exception as err:
    print(err)
    return "해당 날짜의 급식정보가 없어요 ㅠㅠ"

def get_schedule(text):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  YMD = get_ymd(text)

  try:
    if YMD:
      schedule_info = neis.SchoolSchedule(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, AA_YMD=YMD)
    else:
      schedule_info = neis.SchoolSchedule(ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE)

    schedule = schedule_info.EVENT_NM

    return schedule
  except Exception as err:
    print(err)
    return "해당 날짜의 학사일정 정보가 없어요 ㅠㅠ"

def get_timetable(text):
  neis = neispy.SyncClient(force=True)

  AE = "B10" # 교육청 코드
  SE = 7010536 # 학교 코드

  YMD = get_ymd(text)

  try:
    grade_idx = text.index("학년") - 1
    class_idx = text.index("반") - 1
    grade_no = int(text[grade_idx])
    class_no = int(text[class_idx])
  except Exception as e:
    print(f'exception! {e}')
    return "학년 반 정보를 제대로 입력해주세요!"

  try:
    if YMD:
      timetable_info = neis.timeTable(schclass='his', ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, ALL_TI_YMD=YMD, GRADE=grade_no, CLRM_NM=class_no)
    else:
      timetable_info = neis.timeTable(schclass='his', ATPT_OFCDC_SC_CODE=AE, SD_SCHUL_CODE=SE, GRADE=grade_no, CLRM_NM=class_no)

    timetable = [i['ITRT_CNTNT'] for i in timetable_info.data]

    result = ''

    for index, item in enumerate(timetable):
      result += f'{index+1}교시 - {item}\n'
    
    return result
  except Exception as err:
    print(err)
    return "해당 날짜의 시간표 정보가 없어요 ㅠㅠ"

def get_howtouse():
  return """
  사용법은 다음과 같습니다!\n
  1. 급식 찾기\n
  특정 날짜의 급식을 받고싶을 땐 "n월 n일 급식 알려줘" 하면 되고, 오늘 급식은 그냥 "급식 알려줘" 하면 됩니다.\n
  2. 시간표 찾기\n
  "n학년 n반 시간표 알려줘" 하면 됩니다.\n
  특정 날짜의 시간표를 받고 싶을땐, "n월 n일 n학년 n반 시간표 알려줘" 하면 됩니다.\n
  3. 학사일정 찾기\n
  특정 날짜의 학사일정을 받고싶을 땐 "n월 n일 학사일정 알려줘" 하면 되고, 오늘 학사일정은 그냥 "학사일정 알려줘" 하면 됩니다.\n
  """

def get_ymd(text=""):
  try:
    month_idx = text.index("월") - 1
    day_idx = text.index("일") - 1
    month = f"0{text[month_idx]}" if len(text[month_idx]) == 1 else text[month_idx-1:month_idx]
    day = f"0{text[day_idx]}" if len(text[day_idx]) == 1 else text[day_idx-1:day_idx]
    YMD = int(f'{datetime.now().year}{month}{day}')

    return YMD
  except Exception as e:
    print(f'exception! {e}')
    return False


def chat_with_ai(text):
  model = KoGPT2Chat.load_from_checkpoint(args.model_params)
  response = model.chat(text)

  return response

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)