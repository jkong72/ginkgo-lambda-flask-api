from flask import request, render_template, make_response
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

import datetime
from dateutil.relativedelta import relativedelta

class FindIncomeResource(Resource):
    def get(self) :
        today = datetime.date(2021, 12, 31)
        get_data_from = today + relativedelta(months=-6)
        get_data_from = get_data_from.isoformat()
        get_data_to = today + relativedelta(days=+1)
        get_data_to = get_data_to.isoformat()
        
        print(get_data_from)
        print(get_data_to)
        # 나중에  jwt로 바꿀것
        user_id = 1
        try :
            print("db 커넥션 시작")
            connection = get_connection()
            print("db 커넥션 성공")
            # 계좌정보가져오기
            # 2. 쿼리문 
            # 에러 빼고 일단 한다.
            query = '''SELECT * FROM trade
                        where user_id= %s 
                        and inout_type = "입금"
                        and tran_datetime > %s 
                        AND tran_datetime < %s;
                        '''
            record = (user_id,  get_data_from, get_data_to)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            trade_lnfo = cursor.fetchall()

            i = 0
            for record in trade_lnfo:
                
                trade_lnfo[i]['tran_datetime'] = record['tran_datetime'].isoformat()         
                i = i + 1
            
            trade_lnfo

            

        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' :3} , HTTPStatus.BAD_REQUEST

        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        
        return {"error" : 0, "user_info" : user_lnfo, "account_info" : account_lnfo, "trade_info" : trade_lnfo, "type_info" : type_lnfo}


