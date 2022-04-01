    
from flask import request,session
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error  
from utils.hashing_pw import hash_password, check_password
from flask_jwt_extended import create_access_token


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
        return {'error' : 1 , 'result': 'wrong email'}

      
    if check_password(password, record_list[0]['password']) == False :
        # return {'error' : 1, 'result': 'wrong pwd'}, HTTPStatus.BAD_REQUEST
        return {'error' : 1, 'result': 'wrong pwd'}


    user_id = record_list[0]['id']
    access_token = create_access_token(user_id)

    return {'result' : 'success','access_token': access_token} 