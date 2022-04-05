from flask import request, render_template, make_response
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

import datetime
from dateutil.relativedelta import relativedelta

# error 1 = > db에서 유저정보 get하다가 안된것, 2는 계좌, 3은 거래 , 4는 타입

rep_ok = 0
rep_err = 1

class MainPageInfoResource(Resource) :
    @jwt_required()  
    def get(self) :
        today = datetime.date(2021, 12, 31)
        get_data_from = today + relativedelta(months=-1)
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

            query = '''SELECT * FROM trade 
                    where user_id=%s
                    order by tran_datetime desc
                    limit 1;
                    '''
            record = (user_id, )
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            rast_trade_data = cursor.fetchall()

            if len(rast_trade_data) < 1 :
                return {'error' : 9999}

            rast_trade_data = rast_trade_data[0]['tran_datetime']
            rast_trade_date = datetime.date(rast_trade_data.year,rast_trade_data.month, rast_trade_data.day)

            if rast_trade_date < today :
                return {'error' : 8282}
                
            # rast_trade_data[0]['tran_datetime'] = record['tran_datetime'].isoformat()         
            
            

        
        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' :3} , HTTPStatus.BAD_REQUEST



        try :
      
            query = '''SELECT id , expires_date, payday, access_token 
                        FROM ginkgo_db.user
                        where id = %s;
                        '''
            record = (user_id,)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            user_lnfo = cursor.fetchall()
            print(user_lnfo)

            i = 0
            for record in user_lnfo:
                user_lnfo[i]['expires_date'] = record['expires_date'].isoformat()         
                i = i + 1


        except Error as e:
            print('Error ', e)
            return {'error' : 1} 


        try :
            # 계좌정보가져오기
            # 2. 쿼리문 
            query = '''SELECT * FROM account
                        where user_id = %s;
                        '''
            record = (user_id,)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            account_lnfo = cursor.fetchall()
            print(account_lnfo)

        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : 2} , HTTPStatus.BAD_REQUEST
        
        try :
            # 계좌정보가져오기
            # 2. 쿼리문 
            # 에러 빼고 일단 한다.
            query = '''SELECT td.id, td.user_id,td.tran_datetime, td.print_content, td.inout_type, td.tran_amt, td.account_id, tp.basic_type, tp.detail_type
                        FROM (SELECT * FROM trade where user_id=%s and tran_datetime >%s AND tran_datetime < %s) td
                        left join type tp
                        on td.type_id = tp.id;
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
            

            # print(trade_lnfo)

        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' :3} , HTTPStatus.BAD_REQUEST




        try :
            # 계좌정보가져오기
            # 2. 쿼리문 
            query = '''SELECT * FROM type
                        order by id; '''
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, )
            type_lnfo = cursor.fetchall()
            print(type_lnfo)

        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : '1'} , HTTPStatus.BAD_REQUEST

        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        
        return {"error" : 0, "user_info" : user_lnfo, "account_info" : account_lnfo, "trade_info" : trade_lnfo, "type_info" : type_lnfo}
    
    
    @jwt_required()  
    def put(self) :
        user_id = get_jwt_identity()
        data = request.get_json()
        print("request PUT data")
        print(data)
        payday = data['data']
        print(payday)

        try : 
            # 1. DB에 연결
            connection = get_connection()
            # 2. 쿼리문
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
        # finally는 필수는 아니다.
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
                return {'error' : rep_ok}, HTTPStatus.OK
