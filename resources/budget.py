from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection

rep_ok = 0
rep_err = 1


class budgetResource(Resource):
    def get(self):
        # 유저 인증. 방법 생각하기
        # todo 테스트 유저아이디 바꾸기
        user_id = 1
        try :
            # 클라이언트가 GET 요청하면, 이 함수에서 우리가 코드를 작성해 주면 된다.
            
            # 1. db 접속
            connection = get_connection()

            # 2. 해당 테이블, recipe 테이블에서 select
            query = """select b.id, b.user_id, b.title, t.basic_type , t.detail_type, b.amount
                        from budget as b
                        left join type t
                        on user_id = %s and b.type_id = t.id;"""
                                    
            record = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            # select 문은 아래 내용이 필요하다.
            # 커서로 부터 실행한 결과 전부를 받아와라.
            record_list = cursor.fetchall()
            print(record_list)


        # 3. 클라이언트에 보낸다. 
        except Error as e :
            # 뒤의 e는 에러를 찍어라 error를 e로 저장했으니까!
            print('Error while connecting to MySQL', e)
            return {'error' : rep_err, 'content' :str(e)}, HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.

        finally : 
            print('finally')
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return { 'error' : rep_ok, 'count' : len(record_list), 'list' : record_list }, HTTPStatus.OK


    def post(self) : 
        # todo user_id 받아오는것 추가
        user_id = 1

        # body에서 데이터 받아오기
        data = request.get_json()

        try : 
            # 1. DB에 연결
            connection = get_connection()
            # 2. 쿼리문 만들기 : mysql workbench 에서 잘 되는것을 확인한 SQL문을 넣어준다.
            # 이렇게 함수를 쓰면 로컬타임으로 가져온다. 하지만 서버에 저장할때는 UTC로 넣어주어야 한다.

            query = '''insert into budget
                        (user_id, title, type_id, amount)
                        values
                        (%s,%s,%s,%s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = (user_id, data['title'], data['type_id'],data['amount'])
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

        except Error as e:
            print('Error', e)
            return {'error' : rep_err, 'content' :str(e)}, HTTPStatus.BAD_REQUEST
        # finally는 필수는 아니다.
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
            else :
                print('MySQL connection is closed')
        
        return {'error' : rep_ok}, HTTPStatus.OK




