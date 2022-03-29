from flask import request, render_template, make_response
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

# error 1 = > db에서 유저정보 get하다가 안된것, 2는 계좌, 3은 거래 , 4는 타입

class MainPageInfoResource(Resource) :
    def get(self) :
        user_id = 7
        print(user_id)

        try :
            print("db 커넥션 시작")
            connection = get_connection()
            print("db 커넥션 성공")


            # 먼저 유저정보부터 가져오기
            # 2. 쿼리문 
            query = '''SELECT id , expires_date, payday FROM ginkgo_db.user
                        where id = %s;
                        '''
            record = (user_id,)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            user_lnfo = cursor.fetchall()
            print(user_lnfo)


        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : 1} , HTTPStatus.BAD_REQUEST

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
                        FROM (SELECT * FROM trade where user_id = %s) td
                        left join type tp
                        on td.type_id = tp.id;
                        '''
            record = (user_id,)
            
            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            trade_lnfo = cursor.fetchall()

            i = 0
            for record in trade_lnfo:
                
                trade_lnfo[i]['tran_datetime'] = record['tran_datetime'].isoformat()         
                i = i + 1
            

            print(trade_lnfo)

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
