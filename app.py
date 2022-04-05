import json
from flask import Flask, jsonify, make_response, request, render_template, redirect
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

import requests


from resources.login import login_def, register_def
from resources.main_info import MainPageInfoResource
from resources.openBanking import OpenBankingResource
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource , jwt_blacklist
from resources.bank_tran_id import BankTranIdResource
from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from charts.chart1 import chart1
from charts.main_chart import main_chart
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource
from resources.find_income import FindIncomeResource, SetIncomeResource
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


api.add_resource(MainPageInfoResource, '/main/info')                # 메인페이지 정보 불러오기
api.add_resource(FindIncomeResource, '/main/income')                # 월급 추정 



##################################################
# HTML-Front Routing #############################
##################################################
# 샘플 코드입니다.
@app.route('/')
def chart_tester():
    chart1_json = chart1()
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


        # 페이지 이동을 위한 if 문
        # 일단 기본적으로는 메인으로 이동 
        response = make_response(redirect('/main'))       
        # 월급일이 없으면 월급일 지정페이지
        if login_return["decide_page"]["payday"] is None :
            response = make_response(redirect('/main/is_income')) 
        # 오뱅토가 없으면 오뱅토 발급페이지
        if login_return["decide_page"]["access_token"] is None :
            response = make_response(render_template('user/openBanking.html'))

        # 엑세스 토큰 쿠키로 세팅    
        response.set_cookie('jwt_access_token', login_return['access_token'])

        print(access_token)

        # 로그인 성공시 'access_token': access_token 넘김
        return response
    else:
        return render_template('user/login.html')



@app.route('/user/register',methods=['POST','GET'])
def register():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        register_return = register_def(email, password)
        print("register_return")
        print(register_return)

        # wrong eamil or pwd
        if register_return=={'error' : 1 , 'result': 'wrong email'}:
            register_return=register_return['result']
            return render_template('user/register.html', result=register_return)

        elif register_return=={'error' : 1 , 'result': 'wrong password length'}:
            register_return=register_return['result']
            return render_template('user/register.html', result=register_return)
        else :
            register_return['result'] = 'success'

        # 회원가입이 성공적으로 끝나면 로그인 페이지로 넘어간다.    
        return redirect('/user/login')
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
        return redirect('/main/is_income')                    # 오뱅토인증을 막 끝낸사람은 당연히 월급 데이터가 없다. 추측하는 페이지로 전달
    elif openBanking['result']=='인증을 다시 진행해주세요':

        return render_template('user/openBanking.html',result=openBanking)



##################################################

@app.route('/main')
def main_page():
    main_data = main_chart()

    return render_template('main_page.html', data = main_data["data"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"] )


@app.route('/main/is_income',methods=['POST','GET'])
def is_income():
    if request.method == 'GET':
        print("is_income 페이지")
        URL =  Config.LOCAL_URL + "/main/income"
        response = requests.get(URL)
        response = response.json()
        print(response)
        return render_template('is_your_income.html' , income_dict = response["income_dict"])
    if request.method == 'POST':
        selected_radio = request.form.get('comp_select')
        print(selected_radio)
        URL =  Config.LOCAL_URL + "/main/income"
        try :
            data = {'print_content' : selected_radio}
            response = requests.put(URL, json=data)
            response = response.json()
            print(response)
        except:
            print(response)
            return response
        return redirect('/main')
        




@app.route('/main/income_page')
def income_datepicker():
    if request.args.get('date') != None :
        date = request.args.get('date')
        date = int(date[-2:])
        try :
            URL = Config.LOCAL_URL +"/main/info"
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
    app.run()
