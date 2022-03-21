from flask import *
from http import HTTPStatus
from flask_restful import Resource
from numpy import dtype
import requests
from config import *
from flask.json import jsonify

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity
from dateutil.relativedelta import *


#### 고정값
# client_id
# redirect_uri
# scope
# state
# auth_type

#### code 값을 가져온다
# response_type



# ?code=0&client_id=fde4d72d-e26b-492c-9d66-d7ef9014cd59&client_secret=980fb060-8387-4dd1-8f3a-989d3083fe4e&redirect_uri=http://localhost:5000/&grant_type=authorization_code

class testResource(Resource) :
    @jwt_required()
    def get(self) :
        # jwt에서 발행된 토큰 이용
        user_id = get_jwt_identity()
        print('user_id = ',user_id)

        get_code = request.args.get('code')

        
        params = {"code":get_code, "client_id": "fde4d72d-e26b-492c-9d66-d7ef9014cd59", "client_secret": "980fb060-8387-4dd1-8f3a-989d3083fe4e", "redirect_uri":"http://localhost:5000/","grant_type": "authorization_code", }
        # print(params)
        info = requests.post(Config.Token_GET_URL, params=params)
        
        info = info.json()
        print(type(info))
        print(info)
        
        ## expires_in -> sec 단위로 온다.
        ## expires_in -> relativedelta (second=)
        expires_in = info['expires_in']
        expires_date = expires_date+relativedelta(seconds=expires_in)

        try :
            # 1. DB 에 연결
            cnt = get_connection()
           
           
            # 2. 쿼리문 
            query = '''update user SET access_token=%s,  refresh_token=%s, expires_date=%s, user_seq_no=%s where id=%s;'''
            print(query)
            record = (info['access_token'],  info['refresh_token'], expires_date, info['user_seq_no'] , user_id )
            
            
            

            # 커넥션으로부터 커서를 가져온다.
            cursor = cnt.cursor()

            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)




            # 커넥션 커밋.=> 디비에 영구적으로 반영
            cnt.commit()

            # DB에 저장된 유저의 아이디를 가져온다.
            user_id = cursor.lastrowid

            print(user_id)

        except Error as e:
            print('Error ', e)
            return {'error' : '인증을 다시 진행해주세요'} , HTTPStatus.BAD_REQUEST
        finally :
            if cnt.is_connected():
                cursor.close()
                cnt.close()
                print('MySQL connection is closed')

        access_token = info['access_token']
        return {'result': 0, 'access_token':access_token}