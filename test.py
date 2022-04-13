

import requests
from config import Config
from flask import Flask, request

jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0OTgyMzAyNCwianRpIjoiMGYzNmM5ZmQtOWRlNC00M2E5LTgwZWYtMzgxZDY2NTA2Yzk4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6NjQsIm5iZiI6MTY0OTgyMzAyNCwiZXhwIjoxNjQ5ODIzOTI0fQ.-zKkzWBjCfJcVsvTCnYn1879EWCmcmmL7ury8ft0GOw"
# print (jwt)
headers = {"Authorization": "Bearer "+jwt}

url=Config.LOCAL_URL
url = url+'/trade'
last_trade_date = requests.get(url=url, headers=headers).json()

if (len(last_trade_date['data'])) == 0:
    print ('등록된 데이터 없음')

print (len(last_trade_date['data']))
print (last_trade_date)
print ('-'*20)
print (last_trade_date['data'][0]['tran_datetime'])
print (last_trade_date['data'][-1])