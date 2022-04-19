from flask import Flask, jsonify, make_response, request, render_template, redirect, url_for
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus

import requests

import json


from charts.main_chart import main_chart
from resources.login import login_def, register_def, page_def
from resources.main_info import MainPageInfoResource
from resources.openBanking import OpenBankingResource
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource , jwt_blacklist
from resources.bank_tran_id import BankTranIdResource
from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource
from resources.find_income import FindIncomeResource
# from test import getList
from resources.week_info import WeekInfoResource
from charts.chart1 import chart1
from utils.main_utils import first_decide, get_data, second_decide
from utils.regular_trade_detector import regular_trade_detector


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
api.add_resource( UserLogoutResource, '/user/logout')                    # 유저 로그아웃
api.add_resource( OpenBankingResource, '/user/openBanking_resources')    # 오픈뱅킹 토큰 발급

api.add_resource(budgetResource, '/budget')                         # 예산 가져오기 및 추가
api.add_resource(budgetEditResource,  '/budget/<int:budget_id>')    # 예산 수정 및 삭제

api.add_resource(AccountInfoResource, '/account')                   # DB에서 계좌 정보 조회
api.add_resource(TradeInfoResource, '/trade')                       # DB에서 거래 내역 조회

api.add_resource(BankTranIdResource, '/bank_tran_id')               # 은행 거래 코드 입출

api.add_resource(MainPageInfoResource, '/main_info')                # 메인페이지에서 필요한 정보 호출 api

api.add_resource(FindIncomeResource,'/income' )                     # 월급 확인
api.add_resource(WeekInfoResource, '/week_info')                    # 차트에 넣을 일주일 데이터 호출






##################################################
# HTML-Front Routing #############################
##################################################

# 샘플 코드입니다.
@app.route('/')
def route_page():
    return redirect(url_for('login'))



@app.route('/user/login', methods=['POST','GET'])
def login():
    if request.method =='POST':
        # 이메일과 페스워드를 전달받는 코드
        email = request.form['email']
        password = request.form['password']
        # login_def를 이용 로그인 여부를 반환받는다
        login_return = login_def(email, password)

        # 위에서 반환받은 로긍인 여부로 문제가 있다면 클라이언트에 에러메세지 송출
        # wrong eamil or pwd
        if login_return=={'error' : 1 , 'result': 'wrong email'}:
            login_return=login_return['result']
            return render_template('user/login.html', result=login_return)

        elif login_return=={'error' : 1 , 'result': 'wrong pwd'}:
            login_return=login_return['result']
            return render_template('user/login.html', result=login_return)
        # 로그인 성공했을 때 
        else :
            login_return['result'] = ' '
            jwt_access_token = login_return['access_token']
            result = login_return['result']
    
        page_result = page_def(email)
        print( page_result )
        if page_result['user_lnfo'][0]['access_token'] is None :
        
            resp = make_response(render_template('user/openBanking.html',access_token=jwt_access_token, result=result))
            resp.set_cookie('jwt_access_token', login_return['access_token'])
            print(jwt_access_token)
            return resp

        
        else :
            # 메인에 넣을 파라미터들~
            # API 호출 파라미터 정리
            end_point = Config.END_POINT
            # end_point = Config.LOCAL_URL
            url = end_point + '/main_info'
            headers={'Authorization':'Bearer '+jwt_access_token}
            # API 호출 
            main_result = requests.get(url,headers=headers).json()
            # API 호출 결과에 따른 페이지 이동
            print(main_result['error'])

            return second_decide(main_result, jwt_access_token=jwt_access_token)
        
    else:
        return render_template('user/login.html')


@app.route('/user/logout', methods=['POST','GET'])
def logout():
    jwt_access_token = request.cookies.get('jwt_access_token')
    jwt_access_token = None
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
        elif register_return=={'error' : '1', 'result':'This email is already exists'}:
            register_return=register_return['result']
            return render_template('user/register.html', result=register_return)
        else :
            register_return['result'] = 'success'
            register_return = register_return['result']
    
        # test

        # 회원가입이 성공적으로 끝나면 로그인 페이지로 넘어간다.    
        resp = make_response(render_template('user/login.html', result=register_return))

        
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

    print("openBanking['result'] : ")
    print(openBanking['result'])

    # 오픈뱅킹 리소스에서의 result 값으로 띄워주기
    if openBanking['result']=='성공':
        end_point = Config.END_POINT
        # end_point = Config.LOCAL_URL
        get_result = get_data(jwt_access_token)
        if get_result["error"] != 0 :
            print(get_result["error"])

        # 메인에 넣을 파라미터들~
        # API 호출 파라미터 정리
        url = end_point + '/main_info'
        headers={'Authorization':'Bearer '+jwt_access_token}
        # API 호출 
        main_result = requests.get(url,headers=headers).json()
        # API 호출 결과에 따른 페이지 이동
        print(main_result['error'])
       
        return second_decide(main_result, jwt_access_token)
        # 메인 코드 끝
    
    elif openBanking['result']=='인증을 다시 진행해주세요':

        return render_template('user/openBanking.html',result=openBanking)


@app.route('/wealth',methods=['POST','GET'])
def wealth():
    print("this page is wealth")
    # 쿠키로 저장된 jwt 토큰을 가져오기
    jwt_access_token = request.cookies.get('jwt_access_token')
    print(jwt_access_token)


    end_point = Config.END_POINT
    # end_point = Config.LOCAL_URL
    url = end_point + '/week_info'
    headers={'Authorization':'Bearer '+jwt_access_token}
    
    wealth_result = requests.get(url,headers=headers).json()

    chart_data = chart1(wealth_result)
    
    if 'error' in chart_data :
        resp = make_response(render_template('main/test_user.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


    # 지난 거래 내역과 고정 거래 내역 표시
    regular_trade = regular_trade_detector() # 고정거래 가져오기

    end_point = Config.END_POINT
    # end_point = Config.LOCAL_URL
    url = end_point + '/trade'
    normal_trade = requests.get(url=url, headers=headers).json()
    normal_trade = normal_trade['data']
    normal_trade = normal_trade[0:10+1]


    resp = make_response(render_template('chart.html',
    chart1_x=chart_data["chart1_x"],  chart1_y=chart_data["chart1_y"], chart2_x=chart_data["chart2_x"], chart2_y=chart_data["chart2_y"], # 차트 자료
    normal_trade=normal_trade, # 일반 거래
    regular_trade=regular_trade)) # 고정 거래
    resp.set_cookie('jwt_access_token', jwt_access_token)
    return resp



@app.route('/main')
def main_page():
    # 엑세스 토큰 없으면 로그인도 추가하자
    print("this is root page")
    jwt_access_token = request.cookies.get('jwt_access_token')
    print(jwt_access_token)
    end_point = Config.END_POINT
    # end_point = Config.LOCAL_URL
    url = end_point + '/main_info'
    headers={'Authorization':'Bearer '+jwt_access_token}

    main_result = requests.get(url,headers=headers).json()
    return first_decide(main_result, jwt_access_token)


@app.route('/main/income_page')
def income_datepicker():
    if request.args.get('date') != None :
        print("date 파라미터 감지")
        jwt_access_token =  request.cookies.get('jwt_access_token')
        print("income_datepicker : jwt_access_token")
        print(type(jwt_access_token))
        print(jwt_access_token)
        date = request.args.get('date')
        date = int(date[-2:])
        print(date)
        print(type(date))
        try :
            # URL = Config.LOCAL_URL +"/main_info"
            URL = Config.END_POINT +"/main_info"
            print("requests put payment")
            headers={'Authorization':'Bearer '+jwt_access_token}
            body_data = { 'data' : date }
            response = requests.put(URL, json=body_data, headers=headers)
            response = response.json()

        except :
            print("월급일 수정하다 에러남")
            return {'error' : 44}
        return render_template('main/income_date_complete.html')
    else :
        print("income_datepicker : jwt_access_token")
        jwt_access_token =  request.cookies.get('jwt_access_token')
        print(jwt_access_token)
        resp = make_response(render_template('main/income_date.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


@app.route('/main/is_income',methods=['POST','GET'])
def is_income():
    if request.method == 'POST':
        jwt_access_token =  request.cookies.get('jwt_access_token')
        print(jwt_access_token)
        headers={'Authorization':'Bearer '+jwt_access_token}
        selected_radio = request.form.get('comp_select')
        print(selected_radio)
        # URL = Config.LOCAL_URL + "/income"
        URL = Config.END_POINT + "/income"
        try :
            data = {'print_content' : selected_radio}
            response = requests.put(URL, json=data, headers=headers)
            response = response.json()
            print(response)
        except:
            print(response)
            return response
        return redirect(url_for('route_page'))

@app.route('/test',methods=['POST','GET'])
def test():
    jwt_access_token =  request.cookies.get('jwt_access_token')
    print(jwt_access_token)
    get_result = get_data(jwt_access_token)
    if get_result["error"] != 0 :
        print(get_result["error"])
        if get_result["error"] == 6666 :
            result  = "계좌정보 조회에 실패했습니다."
        if get_result["error"] == 4444 :
            result  = "거래내역 조회에 실패했습니다."
        resp = make_response(render_template('main/test_user.html', result))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp

    return redirect(url_for('route_page'))

    
if __name__ == '__main__' :
    app.run()