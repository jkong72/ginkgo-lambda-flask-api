from flask import Flask, jsonify, make_response, request, render_template, redirect
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

import requests

import json
import plotly
import plotly.graph_objects as go


from charts.main_chart import main_chart




end_point = Config.END_POINT
end_point = Config.LOCAL_URL

def first_decide(main_result, jwt_access_token) :
    # Test user 일때 에러를 막기 위해서 설정한 에러값 9999
    if main_result['error'] == 9999 :
        print("THIS IS ERROR 9999")
        resp = make_response(render_template('main/test_user.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp
    # 모든게 정상일때 
    elif main_result['error'] == 0 :
        main_data = main_chart(main_result)
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
        URL =  Config.LOCAL_URL + "/income"
        response = requests.get(URL, headers=headers)
        response = response.json()
        print(response)

        resp = make_response(render_template('main/is_your_income.html', income_dict = response["income_dict"]))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


    # 모든게 정상일때 
    elif main_result['error'] == 0 :
        main_data = main_chart(main_result)
        print(main_data)
        print("월급일멘트")
        print(main_data["payday_ment"])
        resp = make_response(render_template('main/main.html',labels_list = main_data["labels_list"] , parents_list = main_data["parents_list"] ,values_list = main_data["values_list"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"], jwt = jwt_access_token))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


