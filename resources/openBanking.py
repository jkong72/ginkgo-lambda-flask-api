from flask import *
from http import HTTPStatus
from flask_restful import Resource
import requests
from config import *
from flask.json import jsonify

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity
from dateutil.relativedelta import *

class OpenBankingResource(Resource) :
    # @jwt_required() # 이용자 인증 (jwt) 주석 해제 #todo 
    def post(self) :
        user_email = request.get_json()["data"]
        print (user_email)
        # user_id = get_jwt_identity() # 이용자 식별 (jwt 토큰)
        # print('user_id = ',user_id)

        # 파라미터 지정
        get_code = request.args.get('code')
        client_id = "fde4d72d-e26b-492c-9d66-d7ef9014cd59"
        client_secret = "980fb060-8387-4dd1-8f3a-989d3083fe4e"
        redirect_uri = "http://localhost:5000/"
        grant_type = "authorization_code"

        # 오픈뱅킹 액세스 토큰 발급
        params = {"code":get_code, "client_id": client_id, "client_secret": client_secret, "redirect_uri":redirect_uri,"grant_type": grant_type, }
        info = requests.post(Config.Token_GET_URL)
        info = info.json()


        print ('#'*3 + 'print_info' + '#'*10)
        print(info)
        
        ## expires_in -> sec 단위로 온다.
        ## expires_in -> relativedelta (second=)
        expires_in = info['expires_in']
        expires_date = expires_date+relativedelta(seconds=expires_in)

        try :
            # 1. DB 에 연결
            connection = get_connection()

            query = '''select id from user where email = %s;'''

            param = (user_email,)
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            user_id = record_list['id']

            # 2. 쿼리문 
            query = '''update user SET access_token=%s,  refresh_token=%s, expires_date=%s, user_seq_no=%s where id=%s;'''
            print(query)
            record = (info['access_token'],  info['refresh_token'], expires_date, info['user_seq_no'] , user_id )
            
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)


            # 커넥션 커밋.=> 디비에 영구적으로 반영
            connection.commit()

            # DB에 저장된 유저의 아이디를 가져온다.
            user_id = cursor.lastrowid

            print(user_id)

        except Error as e:
            print('Error ', e)
            return {'error' : '인증을 다시 진행해주세요'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        access_token = info['access_token']
        return {'result': 0, 'access_token':access_token}