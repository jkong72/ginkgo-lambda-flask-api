from http import HTTPStatus

from email_validator import EmailNotValidError, validate_email
from flask import request
from flask.json import jsonify
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
from utils import check_password, hash_password


class ReadInfoResource(Resource):

    def post(self) : 

        data = request.get_json()
        # email, password 

        # 2. DB에서 이메일로 해당 유저의 정보를 받아온다.
         
        try :
            connection = get_connection()# DB에 접속한다

            query = '''select * 
                        from ginkgo_db.user
                        where id = %s; '''# mysql의 ginkgo_db.user에서 id값을 받아온다
            record = (123,)
           
            
            cursor = connection.cursor# DB에서 특정 위치를 가리킨다

            cursor.execute(query,record)# 쿼리에 파람을 넣고 실행한다

            record_list = cursor.fetchall()
            print(record_list)
                    
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)} , HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.
        finally :
            print('finally')
            cursor.close()
            if connection.is_connected():
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')

        if __name__=='__main__':
            ReadInfoResource()
