from contextlib import redirect_stderr
import json
from flask import Flask, jsonify, make_response, request, render_template, redirect
from config import Config

from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

from flask_jwt_extended import JWTManager
from resources.login import login_test

from resources.openBanking import OpenBankingResource

from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource 
from resources.user_login import jwt_blacklist

from resources.bank_tran_id import BankTranIdResource

from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from resources.charts.chart1 import chart1
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource
# from test import getList



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
api.add_resource( UserRegisterResource, '/user/register_resource') # 유저 회원가입
api.add_resource( UserLoginResource, '/user/login_resources')      # 유저 로그인
api.add_resource( UserLogoutResource, '/user/logout')     # 유저 로그아웃
api.add_resource( OpenBankingResource, '/')               # 오픈뱅킹 토큰 발급

api.add_resource(budgetResource, '/budget')                         # 예산 가져오기 및 추가
api.add_resource(budgetEditResource,  '/budget/<int:budget_id>')    # 예산 수정 및 삭제

api.add_resource(AccountInfoResource, '/account')                   # DB에서 계좌 정보 조회
api.add_resource(TradeInfoResource, '/trade')                       # DB에서 거래 내역 조회

api.add_resource(BankTranIdResource, '/bank_tran_id')               # 은행 거래 코드 입출


##################################################
# HTML-Front Routing #############################
##################################################
chart1_json = chart1()

# 샘플 코드입니다.
@app.route('/')
def chart_tester():
    return render_template('chart.html', data = chart1_json)

@app.route('/user/login', methods=['POST','GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        login_return = login_test(email, password)
        
        
        
        return render_template('user/login.html',email=email, password=password, result=login_return)
    else:
        return render_template('user/login.html')
    
@app.route('/user/register',methods=['POST','GET'])
def register():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']

        return render_template('user/register.html',email=email, password=password)
    else:
        return render_template('user/register.html')




if __name__ == '__main__' :
    app.run()
