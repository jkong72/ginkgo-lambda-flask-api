from flask import Flask, jsonify, make_response, request, render_template, redirect
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

import requests

import json



from charts.main_chart import main_chart

import json

import pandas as pd
import requests
from http import HTTPStatus
from mysql_connection import get_connection
from mysql.connector.errors import Error
from flask import Flask, jsonify, make_response, request, render_template, redirect
from config import Config
import datetime

from dateutil.relativedelta import relativedelta






end_point = Config.END_POINT
# end_point = Config.LOCAL_URL

def first_decide(main_result, jwt_access_token) :
    # Test user 일때 에러를 막기 위해서 설정한 에러값 9999
    if main_result['error'] == 9999 :
        print("THIS IS ERROR 9999")
        resp = make_response(render_template('main/test_user.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp
    # 모든게 정상일때 
    elif main_result['error'] == 0 :
        main_data = main_chart_data(main_result)
        print("월급일멘트")
        print(main_data["payday_ment"])
        resp = make_response(render_template('main/main.html',labels_list = main_data["labels_list"] , parents_list = main_data["parents_list"] ,values_list = main_data["values_list"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"], jwt = jwt_access_token))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp




def second_decide(main_result, jwt_access_token) :
    # db거래내역이 최신이 아닐때 오픈뱅킹에서부터 데이터 가져오기
    if main_result['error'] == 8282 :
        try :
            get_url =  end_point + "/trade"
            print("get openBanking Trade info start")
            trade_result = requests.post(get_url,headers=headers)
            trade_result = trade_result.json()
            print("get openBanking Trade info end")
        except :
            return  {"error" : 4444}
    # Test user 일때 에러를 막기 위해서 설정한 에러값 9999
    elif main_result['error'] == 9999 :
        print("THIS IS ERROR 9999")
        resp = make_response(render_template('main/test_user.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp

    # payday 가 없을 때 에러
    elif main_result['error'] == 3030 :

        # 월급 질문에 넣을 파라미터
        print("월급일 함수 진입")
        print(jwt_access_token)
        headers={'Authorization':'Bearer '+jwt_access_token}
        # URL = Config.LOCAL_URL + "/income"
        URL = Config.END_POINT + "/income"
        response = requests.get(URL, headers=headers)
        response = response.json()
        print(response)

        resp = make_response(render_template('main/is_your_income.html', income_dict = response["income_dict"]))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


    # 모든게 정상일때 
    elif main_result['error'] == 0 :
        main_data = main_chart_data(main_result)
        print(main_data)
        print("월급일멘트")
        print(main_data["payday_ment"])
        resp = make_response(render_template('main/main.html',labels_list = main_data["labels_list"] , parents_list = main_data["parents_list"] ,values_list = main_data["values_list"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"], jwt = jwt_access_token))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


def main_chart_data(main_result) :
    # 개발 임시 날짜 지정
    today = datetime.date(2021, 12, 31)
    get_data_from = today + relativedelta(months=-1)
    get_data_from = get_data_from.isoformat()
    get_data_to = today + relativedelta(days=+1)
    get_data_to = get_data_to.isoformat()
    
    print(get_data_from)
    print(get_data_to)

    end_point = Config.END_POINT
    # end_point = Config.LOCAL_URL

    
    user_lnfo = main_result["user_info"]
    account_info = main_result["account_info"]
    trade_info = main_result["trade_info"]
    type_info = main_result["type_info"]


    # 차트 만들 데이터 정리
    df = pd.DataFrame(trade_info)
    userChart2 = False

    # 나중에 보낼 지출 총액, 수입 총액
    money_dict = {}
    money_dict["income"] = df.loc[df['inout_type']=='입금', 'tran_amt'].sum()
    money_dict["outcome"] = df.loc[df['inout_type']=='출금', 'tran_amt'].sum()

    if money_dict["income"] - money_dict["outcome"] < 0 :
        userChart2 = True

    values_dict = df.groupby('detail_type')['tran_amt'].sum().to_dict()
    
    
    # 차트에 넣을 라벨과 부모라벨을 리스트에 담는 과정
    # 사용자가 쓴 타입의 라벨 == labels_list, 그 라벨의 부모(basic_type) 은 parents_list
    labels_list = list(values_dict.keys())
    if '급여' in labels_list :
        userChart2 == True
    type_df = pd.DataFrame(type_info)

    if userChart2 == False :

        # 디테일 타입으로부터 베이식 타입 추출을 위한 딕셔너리
        set_type_dic = type_df[['basic_type', 'detail_type']].set_index('detail_type').to_dict('index')
        
        # 1차 디테일 타입으로부터 베이식 타입 추출
        parents_list = []
        for label in labels_list :
            parents_list.append(set_type_dic[label]['basic_type'])

        # 2차 다듬기 베이식 분류는 부모를 급여로, 급여는 부모가 없는 것으로 수정
        for i in range(len(labels_list)):
            if labels_list[i] != '급여':
                if labels_list[i] == parents_list[i]:
                    parents_list[i] = '급여'                                               
            else :
                parents_list[i] = ''

        
        # 사용자가 라벨별로 쓴금액 값 리스트에 담기
        values_list = list(values_dict.values())

        # parents_list 에는 있는데 라벨에 없는경우 추가해주는 코드
        complement = list(set(parents_list) - set(labels_list))

        complement.remove('')
        print(complement)
        for label in complement :
            labels_list.append(label)
            parents_list.append('급여')
            values_list.append(int(df.loc[df['basic_type'] == label, 'tran_amt'].sum()))


        print(labels_list)
        print(parents_list)
        print(values_list)


    if userChart2 == True :
         # 디테일 타입으로부터 베이식 타입 추출을 위한 딕셔너리
        set_type_dic = type_df[['basic_type', 'detail_type']].set_index('detail_type').to_dict('index')
        
        # 1차 디테일 타입으로부터 베이식 타입 추출
        parents_list = []
        for label in labels_list :
            parents_list.append(set_type_dic[label]['basic_type'])

        # 2차 다듬기 베이식 분류는 부모를 총지출로
        for i in range(len(labels_list)):
            if labels_list[i] != '총지출':
                if labels_list[i] == parents_list[i]:
                    parents_list[i] = '총지출'       

        # 사용자가 라벨별로 쓴금액 값 리스트에 담기
        values_list = list(values_dict.values())   

        # parents_list 에는 있는데 라벨에 없는경우 추가해주는 코드
        complement = list(set(parents_list) - set(labels_list))   
        complement.remove('총지출')

        for label in complement :
            labels_list.append(label)
            parents_list.append('총지출')
            values_list.append(int(df.loc[df['basic_type'] == label, 'tran_amt'].sum()))
        
        print(labels_list)
        print(parents_list)
        print(values_list)

        # 마지막으로 급여대신 총 지출을 리스트에 집어넣는 과정
        labels_list.append('총지출')
        parents_list.append('')
        values_list.append(money_dict["outcome"])

    # 유저 이름 뽑아내기
    user_name = account_info[0]['account_holder_name']


    # 계좌 정보에서 핀테크 번호로 잔액조회 돌리기
    # 기존 current_time = datetime.now() 에서 변경 ## 추후 today를 변경시 변경
    current_time = today
    current_time = current_time.strftime("%Y%m%d%H%M%S")
    print(current_time)
    print(type(current_time))
    i = 0
    amt_sum = 0
    for account in account_info :
        try :
            URL = end_point + "/bank_tran_id"
            print("requests bankTranId")
            bankTranId = requests.post(URL)
            bankTranId = bankTranId.json()
            print(bankTranId)
            print("I`m get bankTranId")
        except :
            print("I`m error of bankTranId")
            return {'error' : 44}

        OBURL = "https://testapi.openbanking.or.kr/v2.0/account/balance/fin_num"
        print(account["fintech_num"])
        params = {"bank_tran_id" : bankTranId, "tran_dtime": current_time, "fintech_use_num" : account["fintech_num"]}
        headers = {"Authorization" : "Bearer " + user_lnfo[0]["access_token"]}
        try :
            response = requests.get(OBURL, headers=headers, params=params)
            response = response.json()
            
            print(type(response))
            print(response)

            account_info[i]["balance_amt"] = response["balance_amt"]
            amt_sum = amt_sum + int(response["balance_amt"])

            i = i + 1
            
        except :
            return  {"error" : 4444}
    
    print(account_info)
    money_dict["amt_sum"] = amt_sum
    print(money_dict)
    


    # 월급일 기준으로 거래 데이터 가져올 기준 정하기
    payday = user_lnfo[0]['payday']

    if payday is not None :
        today = datetime.date(2021, 12, 31)
        real_today = datetime.date.today()
        print("real_today")
        print(real_today)
        year = real_today.year
        month = real_today.month
        day = real_today.day

        
        if day - payday < 0 :
            d_day =  payday - day  
        
        else :
            next_payday = datetime.date(year, month, payday) + relativedelta(months=+1)
            print("next_payday")
            print(next_payday)
            d_day = (next_payday - real_today).days

        payday_ment = "월급까지 D-{}".format(d_day)
    
    else : 
         payday_ment = "월급일을 입력해주세요"



    # data = 차트.json
    return {"name" : user_name, "payday_ment" : payday_ment, 'account_info' : account_info, "money_dict" : money_dict, "labels_list" :labels_list, "parents_list": parents_list, "values_list": values_list}



def get_data(jwt_access_token) :
    headers={'Authorization':'Bearer '+jwt_access_token}
    try :
        get_url =  end_point + "/account"
        print("get openBanking account info start")
        account_result = requests.post(get_url,headers=headers)
        account_result = account_result.json()
        print("get openBanking account info end")
    except :
        return  {"error" : 6666}
    
    # 오픈뱅킹에서부터 데이터 가져와서 db거래내역 테이블에 저장
    try :
        get_url =  end_point + "/trade"
        print("get openBanking Trade info start")
        trade_result = requests.post(get_url,headers=headers)
        trade_result = trade_result.json()
        print("get openBanking Trade info end")
    except :
        return  {"error" : 4444}
    
    return {"error" : 0}