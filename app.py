from flask import Flask, jsonify, make_response, request, render_template, redirect
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

import requests


from resources.login import login_def, register_def
from resources.openBanking import OpenBankingResource
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource , jwt_blacklist
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
api.add_resource( UserRegisterResource, '/user/register_resource')  # 유저 회원가입
api.add_resource( UserLoginResource, '/user/login_resources')       # 유저 로그인
api.add_resource( UserLogoutResource, '/user/logout')               # 유저 로그아웃
api.add_resource( OpenBankingResource, '/user/openBanking_resources')    # 오픈뱅킹 토큰 발급

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
        login_return = login_def(email, password)

        # wrong eamil or pwd
        if login_return=={'error' : 1 , 'result': 'wrong email'}:
            login_return=login_return['result']
            return render_template('user/login.html', result=login_return)

        elif login_return=={'error' : 1 , 'result': 'wrong pwd'}:
            login_return=login_return['result']
            return render_template('user/login.html', result=login_return)
        else :
            login_return['result'] = ' '
            access_token = login_return['access_token']
            result = login_return['result']
    
        
        resp = make_response(render_template('main.html',access_token=access_token, result=result))
        resp.set_cookie('jwt_access_token', login_return['access_token'])

        print(access_token)

        # 로그인 성공시 'access_token': access_token 넘김
        return resp
    else:
        return render_template('user/login.html')



@app.route('/user/register',methods=['POST','GET'])
def register():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        register_return = register_def(email, password)

        # wrong eamil or pwd
        if register_return=={'error' : 1 , 'result': 'wrong email'}:
            register_return=register_return['result']
            return render_template('user/register.html', result=register_return)

        elif register_return=={'error' : 1 , 'result': 'wrong password length'}:
            register_return=register_return['result']
            return render_template('user/register.html', result=register_return)
        else :
            register_return['result'] = 'success'
            access_token = register_return['access_token']
            result = register_return['result']
    
        # test

        # 회원가입이 성공적으로 끝나면 로그인 페이지로 넘어간다.    
        resp = make_response(render_template('user/login.html',access_token=access_token, result=result))
        resp.set_cookie('jwt_access_token', register_return['access_token'])

        print(access_token)

        # 로그인 성공시 'access_token': access_token 넘김
        return resp
    else:
        return render_template('user/register.html')




@app.route('/user/openBanking', methods=['POST','GET'])
def open_token():
    # URL 에서 code 뒷 부분만 가져오기
    get_code = request.args.get('code')


    # 쿠키로 저장된 jwt 토큰을 가져오기
    jwt_access_token = request.cookies.get('jwt_access_token')
    print(jwt_access_token)

    # 오픈뱅킹 리소스에 jwt 토큰 보내주기
    OPENBANKING_URL='http://localhost:5000/user/openBanking_resources'
    headers={'Authorization':'Bearer '+jwt_access_token}
    params={"code":get_code}

    openBanking = requests.post(OPENBANKING_URL,headers=headers,params=params)

    openBanking = openBanking.json()
    

    # 오픈뱅킹 리소스에서의 result 값으로 띄워주기
    if openBanking['result']=='성공':
        return render_template('main.html')
    elif openBanking['result']=='인증을 다시 진행해주세요':

        return render_template('user/openBanking.html',result=openBanking)





if __name__ == '__main__' :
    app.run()
