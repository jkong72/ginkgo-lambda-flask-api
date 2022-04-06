from flask import Flask, jsonify, make_response, request, render_template, redirect, url_for
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from config import Config
from flask.json import jsonify
from flask_restful import Api
from http import HTTPStatus
import requests
import json
import plotly
import plotly.graph_objects as go


from resources.login import login_def, register_def
from resources.main_info import MainPageInfoResource
from resources.openBanking import OpenBankingResource
from resources.user_login import UserLoginResource, UserLogoutResource, UserRegisterResource , jwt_blacklist
from resources.bank_tran_id import BankTranIdResource
from resources.budget.budget import budgetResource
from resources.budget.budget_edit import budgetEditResource
from resources.trade.trade_upload import AccountInfoResource, TradeInfoResource
# from test import getList

from charts.main_chart import main_chart

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

api.add_resource(MainPageInfoResource, '/main_info')                # 메인페이지에 필요한 정보 호출


api.add_resource(AccountInfoResource, '/account')                   # DB에서 계좌 정보 조회
api.add_resource(TradeInfoResource, '/trade')                       # DB에서 거래 내역 조회

api.add_resource(BankTranIdResource, '/bank_tran_id')               # 은행 거래 코드 입출







##################################################
# HTML-Front Routing #############################
##################################################

# 샘플 코드입니다.
@app.route('/')
def root_page():
    # 엑세스 토큰 없으면 로그인도 추가하자
    print("this is root page")
    jwt_access_token = request.cookies.get('jwt_access_token')
    print(jwt_access_token)
    end_point = Config.END_POINT
    end_point = Config.LOCAL_URL
    url = end_point + '/main_info'
    headers={'Authorization':'Bearer '+jwt_access_token}
    
    main_result = requests.get(url,headers=headers).json()
    # print(main_result)
    if main_result['error'] == 5050 :
        resp = make_response(render_template('user/openBanking.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp
    elif main_result['error'] == 3030 :
        resp = make_response(render_template('main/is_your_income.html'))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp

    elif main_result['error'] == 8282 :
        try :
            get_url =  end_point + "/trade"
            print("get openBanking Trade info start")
            trade_result = requests.post(get_url,headers=headers)
            trade_result = trade_result.json()
            print("get openBanking Trade info end")
        except :
            return  {"error" : 4444}

    elif main_result['error'] == 9999 :
        print("THIS IS ERROR 9999")
        account_info = [{"bank_name": "농협" , "account_num_masked": "302-5269-****-**", "balance_amt" : 1000000}]
        money_dict = {"income" : 2000000 , "outcome" : 1250000, "amt_sum": 1000000 }
        payday_ment = "월급일까지 D-20"

        user_name = "테스트 유저"
        labels_list = ['OTT', '급여', '마트', '병원', '온라인쇼핑', '통신비', '보건']
        parents_list = ['급여', '', '급여', '보건', '급여', '급여', '급여']
        values_list =[10000, 500000, 100000, 100000, 150000, 40000, 100000]
        fig =go.Figure(go.Sunburst(
            labels=labels_list,
            parents=parents_list,
            values=values_list,
            branchvalues="total"
        ))
        fig.update_layout(margin = dict(t=0, l=0, r=0, b=0), height=800)
        result = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        resp = make_response(render_template('main/main.html',data = result, name = user_name, payday_ment = payday_ment, account_info= account_info,money_dict = money_dict))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp


    elif main_result['error'] == 0 :
        main_data = main_chart(main_result)
        resp = make_response(render_template('main/main.html',  data = main_data["data"], name= main_data["name"], payday_ment= main_data["payday_ment"], account_info = main_data["account_info"], money_dict = main_data["money_dict"]))
        resp.set_cookie('jwt_access_token',jwt_access_token )
        return resp
    


    return render_template('main.html')

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
    
        
        resp = make_response(redirect('/'))
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
        resp = make_response(redirect('/'))
        resp.set_cookie('jwt_access_token', jwt_access_token)
        return resp
    elif openBanking['result']=='인증을 다시 진행해주세요':

        return render_template('user/openBanking.html',result=openBanking)


@app.route('/wealth')
def wealth():
    pass

@app.route('/user/logout')
def logout():
    pass


if __name__ == '__main__' :
    app.run()
