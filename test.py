from email import header
from flask_restful import Resource
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import config
import datetime as dt
from flask import request
from dateutil.relativedelta import relativedelta

from mysql_connection import get_connection
from utils.openBanking_req import get_account, get_trade

try:
    connection = get_connection()

    query = '''select tran_datetime
                from trade
                order by tran_datetime desc
                limit 1'''

    # 커넥션으로부터 커서를 가져온다.
    cursor = connection.cursor(dictionary = True)
    # 쿼리문을 커서에 넣어서 실행한다.
    cursor.execute(query, )
    result = cursor.fetchall()


except Error as e:
    print('Error ', e)
    # 6. email이 이미 DB에 있으면,
    #    이미 존재하는 회원이라고 클라이언트에 응답한다.

finally :
    if connection.is_connected():
        cursor.close()
        connection.close()
        print('MySQL connection is closed')


print (result)
result=result[0]['tran_datetime'].strftime('%Y%m%d')

print (result)


