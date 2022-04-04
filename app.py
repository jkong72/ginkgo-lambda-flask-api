from urllib import response
from flask import Flask, jsonify, make_response, request, render_template, redirect
from charts.main_chart import main_chart
from config import Config

from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

from flask_jwt_extended import JWTManager
from resources.find_income import FindIncomeResource
from resources.main_info import MainPageInfoResource

from resources.openBanking import OpenBankingResource

from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource 
from resources.user_login import jwt_blacklist

from resources.bank_tran_id import BankTranIdResource
from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource

import requests

from charts.chart1 import chart1


##################################################
# 실제 개발 부분 ##################################
##################################################
app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)


# jwt 토큰
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)


##################################################
# Restful API Resources ##########################
##################################################

# 경로와 리소스를 연결한다.
api.add_resource( UserRegisterResource, '/user/register') # 유저 회원가입
api.add_resource( UserLoginResource, '/user/login2')      # 유저 로그인
api.add_resource( UserLogoutResource, '/user/logout')     # 유저 로그아웃
api.add_resource( OpenBankingResource, '/')               # 오픈뱅킹 토큰 발급

api.add_resource(budgetResource, '/budget')                         # 예산 가져오기 및 추가
api.add_resource(budgetEditResource,  '/budget/<int:budget_id>')    # 예산 수정 및 삭제

api.add_resource(AccountInfoResource, '/account')                   # DB에서 계좌 정보 조회
api.add_resource(TradeInfoResource, '/trade')                       # DB에서 거래 내역 조회

api.add_resource(BankTranIdResource, '/bank_tran_id')               # 은행 거래 코드 입출

api.add_resource(MainPageInfoResource, '/main/info')                # 메인페이지 정보 불러오기
api.add_resource(FindIncomeResource, '/main/income')                # 월급 추정 / 수정 API 


##################################################
# HTML-Front Routing #############################
##################################################



# 샘플 코드입니다.
@app.route('/')
def chart_tester():
    chart1_json = chart1()
    return render_template('chart.html', data = chart1_json)

@app.route('/main')
def main_page():
    main_data = main_chart()
    
    
    
    # if   main_data["payday_ment"] == "월급일을 입력해주세요" :
        
        
        
    #     return redirect('/main/is_income')
        

    return render_template('main_page.html', data = main_data["data"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"] )


@app.route('/main/is_income')
def is_income():
    URL =  Config.LOCAL_URL + "/main/income"
    response = requests.get(URL)
    response = response.json()
    print(response)
    return render_template('is_your_income.html' , income_dict = response["income_dict"])



@app.route('/main/income_page')
def income_datepicker():
    if request.args.get('date') != None :
        date = request.args.get('date')
        date = int(date[-2:])
        try :
            URL = Config.LOCAL_URL +"/main/income"
            print("requests put payment")
            body_data = { 'data' : date }
            response = requests.put(URL, json=body_data)
            response = response.json()

        except :
            print("I`m error of bankTranId")
            return {'error' : 44}
        return render_template('income_complete.html')
    else :
        return render_template('income_page.html')




if __name__ == '__main__' :
    app.run(debug=True)
