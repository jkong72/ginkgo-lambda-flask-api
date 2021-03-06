from flask import request,session
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error  
from utils.hashing_pw import hash_password, check_password
from flask_jwt_extended import create_access_token

from email_validator import validate_email, EmailNotValidError


def login_def(email, password):    
    email = request.form['email']
    password= request.form['password']
    try :
        cnt = get_connection()
        # access_token -> 오픈뱅킹 토큰
        query = '''select id, email, password, access_token ,created_at
                    from user
                    where email = %s; '''
        
        param = (email, )
        
        cursor = cnt.cursor(dictionary = True)

        cursor.execute(query, param)

        # select 문은 아래 내용이 필요하다.
        record_list = cursor.fetchall()
        print(record_list)

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
        if cnt.is_connected():
            cnt.close()
            print('MySQL connection is closed')
        else :
            print('connection does not exist')


    if len( record_list ) == 0 :
        # return {'error' : 1 , 'result': 'wrong email'}, HTTPStatus.BAD_REQUEST
        return {'error' : 1 , 'result': '잘못된 이메일입니다.'}

      
    if check_password(password, record_list[0]['password']) == False :
        # return {'error' : 1, 'result': 'wrong pwd'}, HTTPStatus.BAD_REQUEST
        return {'error' : 1, 'result': '잘못된 비밀번호입니다.'}


    user_id = record_list[0]['id']
    access_token = create_access_token(user_id)

    return {'result' : 'success','access_token': access_token} 



def register_def(email, password):
    email = request.form['email']
    password= request.form['password']
    print(email,password)
    
    # email, password

    #   이메일 주소가 제대로 된 주소인지 확인하는 코드
    #   잘못된 이메일주소면, 잘못됐다고 응답한다.
    try:
        # Validate.
        validate_email(email)
        
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        print(str(e))
        return {'error' : 1 , 'result': '잘못된 이메일입니다.'}

    if (len( password ) < 7 or len(password) > 13):
        return {'error' : 1 , 'result': '잘못된 비밀번호입니다.'}

    # 4. 비밀번호를 암호화한다.
    hashed_password = hash_password(password)

    print(hashed_password)
    print('암호화된 비번 길이 ' + str( len(hashed_password) ))

    #   데이터 DB에 저장.
    #   DB 에 연결
    cnt = get_connection()

    #   중복된 입력값인지 확인
    try:
        query = ''' select email,created_at from ginkgo_db.user where email=%s'''

        #   커서
        param = (email, )
        cursor = cnt.cursor(dictionary = True)
        cursor.execute(query,param)

        # select 문은 아래 내용이 필요하다.
        record_list = cursor.fetchall()
        print(record_list)

        i = 0
        for record in record_list:
            record_list[i]['created_at'] = record['created_at'].isoformat()           
            i = i + 1
        
    except Error as e:
        print('Error ', e)
        return {'error' : '1', 'result':'이미 존재하는 이메일입니다.'}


    #   user테이블에 입력값 insert
    try :
    
        #   쿼리문 
        query = '''insert into user
                    (email, password)
                    values
                    (%s, %s);'''
        record = (email, hashed_password)
        
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
        #   email이 이미 DB에 있으면,
        #   이미 존재하는 회원이라고 클라이언트에 응답한다.
        return {'error' : '1', 'result':'This email is already exists'} 
    finally :
        if cnt.is_connected():
            cursor.close()
            cnt.close()
            print('MySQL connection is closed')

    # 모든것이 정상이면, 회원가입 잘 되었다고 응답.
    return {'result' : 'success'}


def page_def (email) :
    is_error = False
    try :
        print("db 커넥션 시작")
        connection = get_connection()
        print("db 커넥션 성공")

        query = '''SELECT id , expires_date, payday, access_token 
                    FROM ginkgo_db.user
                    where email = %s;
                    '''
        record = (email,)
        
        # 커넥션으로부터 커서를 가져온다.
        cursor = connection.cursor(dictionary = True)
        # 쿼리문을 커서에 넣어서 실행한다.
        cursor.execute(query, record)
        user_lnfo = cursor.fetchall()
        print(user_lnfo)

        if user_lnfo[0]['expires_date'] is not None :
            i = 0
            for record in user_lnfo:
                user_lnfo[i]['expires_date'] = record['expires_date'].isoformat()         
                i = i + 1
        

            

    except Error as e:
        print('Error ', e)
        is_error = True


    finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')

            if is_error == True :
                return {'error' : 1} 
            
            return {'error' : 0, 'user_lnfo' : user_lnfo}