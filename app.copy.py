from flask import Flask, jsonify, make_response, request, render_template, redirect
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
    return redirect('/user/login')



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
                # URL =  Config.LOCAL_URL + "/income"
                URL = Config.END_POINT + "/income"
                response = requests.get(URL, headers=headers)
                response = response.json()
                print(response)

                resp = make_response(render_template('main/is_your_income.html', income_dict = response["income_dict"]))
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
        # 오픈뱅킹에서부터 데이터 가져와서 db계좌정보 테이블에 저장
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


        # 메인에 넣을 파라미터들~
        # API 호출 파라미터 정리
        url = end_point + '/main_info'
        headers={'Authorization':'Bearer '+jwt_access_token}
        # API 호출 
        main_result = requests.get(url,headers=headers).json()
        # API 호출 결과에 따른 페이지 이동
        print(main_result['error'])
        #payday 가 없을 때 에러
        if main_result['error'] == 3030 :
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

       
        # Test user 일때 에러를 막기 위해서 설정한 에러값 9999
        elif main_result['error'] == 9999 :
            
            resp = make_response(render_template('main/test_user.html'))
            resp.set_cookie('jwt_access_token',jwt_access_token )
            return resp

        # 모든게 정상일때 
        elif main_result['error'] == 0 :
            main_data = main_chart(main_result)
            resp = make_response(render_template('main/main.html',  data = main_data["data"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"]))
            resp.set_cookie('jwt_access_token',jwt_access_token )
            return resp

        # 남은 경우 혹시몰라서 설정한 메인 페이지
        return render_template('main.html')
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

    print(chart_data)
    resp = make_response(render_template('chart.html', chart1_x=chart_data["chart1_x"],  chart1_y=chart_data["chart1_y"], chart2_x=chart_data["chart2_x"], chart2_y=chart_data["chart2_y"]))
    resp.set_cookie('jwt_access_token', jwt_access_token)
    return resp



@app.route('/main' ,  methods=['POST','GET'])
def main_page():
    if request.method =='GET':
        # 엑세스 토큰 없으면 로그인도 추가하자
        print("this is root page")
        jwt_access_token = request.cookies.get('jwt_access_token')
        print(jwt_access_token)
        end_point = Config.END_POINT
        # end_point = Config.LOCAL_URL
        url = end_point + '/main_info'
        headers={'Authorization':'Bearer '+jwt_access_token}

        main_result = requests.get(url,headers=headers).json()
        if main_result['error'] == 9999 :
            print("THIS IS ERROR 9999")

            resp = make_response(render_template('main/test_user.html'))
            resp.set_cookie('jwt_access_token',jwt_access_token )
            return resp


        elif main_result['error'] == 0 :
            main_data = main_chart(main_result)
            resp = make_response(render_template('main/main.html',  data = main_data["data"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"]))
            resp.set_cookie('jwt_access_token',jwt_access_token )
            return resp


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
        jwt_access_token =  request.args.get('jwt')
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
        # URL =  Config.LOCAL_URL + "/income"
        URL = Config.END_POINT + "/income"
        try :
            data = {'print_content' : selected_radio}
            response = requests.put(URL, json=data, headers=headers)
            response = response.json()
            print(response)
        except:
            print(response)
            return response
        return redirect('/main')

if __name__ == '__main__' :
    app.run()