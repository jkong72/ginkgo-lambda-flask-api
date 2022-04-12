from flask import request, render_template, make_response
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus
import pandas as pd

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

import datetime
from dateutil.relativedelta import relativedelta



rep_ok = 0
rep_err = 1


class FindIncomeResource(Resource):
    @jwt_required()   
    def get(self) :
        today = datetime.date(2021, 12, 31)
        get_data_from = today + relativedelta(months=-5)
        get_data_from = get_data_from.isoformat()
        get_data_to = today + relativedelta(days=+1)
        get_data_to = get_data_to.isoformat()
        
        print(get_data_from)
        print(get_data_to)
        # 나중에  jwt로 바꿀것
        user_id = get_jwt_identity()
        try :
            print("db 커넥션 시작")
            connection = get_connection()
            print("db 커넥션 성공")
            # 계좌정보가져오기
            # 2. 쿼리문 
            # 에러 빼고 일단 한다.
            query = '''SELECT print_content, tran_amt , count(*) as cnt
                        FROM trade
                        where user_id= %s
                        and inout_type = "입금"
                        and tran_datetime > %s
                        AND tran_datetime < %s
                        group by print_content
                        having cnt > 4 and cnt < 7 
                        order by tran_amt desc;
                        '''
            record = (user_id,  get_data_from, get_data_to)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            income_lnfo = cursor.fetchall()

            income_dict = {}
            for content in income_lnfo :
                income_dict[content["print_content"]] = content["tran_amt"]


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

        
        return {"error" : 0, "income_dict" :  income_dict}
        
    @jwt_required()
    def put(self) :
        user_id =get_jwt_identity()
        data = request.get_json()
        print("request PUT data")
        print(data)
        print_content = data['print_content']

        try : 
            # 1. DB에 연결
            connection = get_connection()

            # classification_type 에 저장
            query = '''insert into classification_type
                    (user_id, type_id, print_content)
                    values
                    (%s, %s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = (user_id, 1 ,print_content)
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error', e)
            return {'error' : rep_err, 'content' :str(e)}
  

        try :    
            # 2. 쿼리문
            query = '''update trade
                        set type_id = %s
                        where user_id = %s and print_content = %s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = ( 1,  user_id, print_content)
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()
            print("커밋완료~")

        except Error as e:
            print('Error', e)
            return {'error' : rep_err}
       
        try :
            query = '''SELECT tran_datetime
                        FROM ginkgo_db.trade
                        where user_id = %s and print_content = %s
                        order by tran_datetime desc
                        limit 1;
                            '''
            record = (user_id, print_content)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            record_list = cursor.fetchall()

            last_income  = record_list[0]['tran_datetime']
            payday= last_income.day


        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' :3} , HTTPStatus.BAD_REQUEST

        try:
            query = '''update user
                            set payday = %s
                            where id =%s;'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = ( payday , user_id)
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()
            print("커밋완료~")

        except Error as e:
            print('Error', e)
            return {'error' : rep_err}, HTTPStatus.BAD_REQUEST


        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
                return {'error' : rep_ok}, HTTPStatus.OK




    