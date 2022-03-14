from flask import request
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from email_validator import validate_email, EmailNotValidError
from utils import hash_password, check_password
from flask_jwt_extended import create_access_token
from flask_jwt_extended.view_decorators import jwt_required
from flask_jwt_extended import get_jwt


class UserRegisterResource(Resource) :
    def post(self) :
        data = request.get_json()
        # email, password

        # 2. 이메일 주소가 제대로 된 주소인지 확인하는 코드
        #    잘못된 이메일주소면, 잘못됐다고 응답한다.
        try:
            # Validate.
            validate_email(data['email'])
            
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error' : '이메일 주소가 잘못되었습니다.'} ,HTTPStatus.BAD_REQUEST

        # 3. 비밀번호 길이같은 조건이 있는지 확인하는 코드
        #    잘못됐으면, 클라이언트에 응답한다.
        if len( data['password'] ) < 8 :
            return {'error' : '비밀번호 길이를 확인하세요'}, HTTPStatus.BAD_REQUEST

        # 4. 비밀번호를 암호화한다.
        hashed_password = hash_password(data['password'])

        print(hashed_password)
        print('암호화된 비번 길이 ' + str( len(hashed_password) ))

        # 5. 데이터를 DB에 저장한다.
        try :
            # 1. DB 에 연결
            connection = get_connection()
           
            # 2. 쿼리문 만들고
            query = '''insert into user
                        (email, password)
                        values
                        (%s, %s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭
            # 써준다.
            record = (data['email'], hashed_password)
            
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다.=> 디비에 영구적으로 반영하라는 뜻.
            connection.commit()

            # DB에 저장된 유저의 아이디를 가져온다.
            user_id = cursor.lastrowid

            print(user_id)

        except Error as e:
            print('Error ', e)
            # 6. username이나 email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' : '이미 존재하는 회원입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

        # 7. JWT 토큰을 발행한다.
        ### DB 에 저장된 유저 아이디값으로 토큰을 발행한다!
        
        access_token = create_access_token(user_id)

        # 8. 모든것이 정상이면, 회원가입 잘 되었다고 응답한다.
        return {'result' : '회원가입이 잘 되었습니다.', 
                'access_token' : access_token}


class UserLoginResource(Resource) :
    def post(self) : 

        data = request.get_json()
        # email, password

        # 2. DB에서 이메일로 해당 유저의 정보를 받아온다.
         
        try :
            connection = get_connection()

            query = '''select * 
                        from user
                        where email = %s; '''
            
            param = (data['email'], )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            ### 중요. 파이썬의 시간은, JSON으로 보내기 위해서
            ### 문자열로 바꿔준다.
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = record['created_at'].isoformat()                
                i = i + 1
            
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

        # 2-1. 만약 없는 이메일 주소로 DB에 요청했을땐
        #      데이터가 없으므로, 클라이언트에게 
        #      회원가입 되어있지 않다고, 응답한다.
        if len( record_list ) == 0 :
            return {'error' : '회원가입 되어있지 않은 사람입니다.'}, HTTPStatus.BAD_REQUEST

        # 3. 클라이언트로부터 받은 비번과, DB에 저장된 비번이
        #    동일한지 체크한다.        
        if check_password(data['password'], record_list[0]['password']) == False :
            # 4. 다르면, 비번 틀렸다고 클라이언트에 응답한다.
            return {'error' : '비밀번호가 다릅니다.'}, HTTPStatus.BAD_REQUEST

        # 5. JTW 인증 토큰을 만들어준다.
        #    유저 아이디를 가지고 인증토큰을 만든다.
        user_id = record_list[0]['id']
        access_token = create_access_token(user_id)

        return {'result' : '로그인이 되었습니다.', 'access_token' : access_token}



jwt_blacklist = set()

# 로그아웃 클래스 
class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
        jti = get_jwt()['jti']
        print(jti)
        # 로그아웃된 토큰의 아이디값을, 블랙리스트에 저장한다.
        jwt_blacklist.add(jti)

        return {'result':'로그아웃 되었습니다.'}