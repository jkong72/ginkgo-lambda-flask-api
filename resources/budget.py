from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity

from mysql_connection import get_connection


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
            query = """select b.id, b.user_id, b.title, t.content as type_name, b.amount
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

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            # i = 0
            # for record in record_list:
            #     record_list[i]['created_at'] = record['created_at'].isoformat()
            #     record_list[i]['updated_at'] = record['updated_at'].isoformat()
            #     i = i +1

        # 3. 클라이언트에 보낸다. 
        except Error as e :
            # 뒤의 e는 에러를 찍어라 error를 e로 저장했으니까!
            print('Error while connecting to MySQL', e)
            return {'error' : str(e)}, HTTPStatus.BAD_REQUEST
        # finally 는 try에서 에러가 나든 안나든, 무조건 실행하라는 뜻.

        finally : 
            print('finally')
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
            else :
                print('connection does not exist')
        return { 'error' : 0, 'count' : len(record_list), 'list' : record_list }, HTTPStatus.OK
