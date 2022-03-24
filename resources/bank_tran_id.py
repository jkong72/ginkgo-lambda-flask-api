import requests
import datetime as dt
from flask_restful import Resource
from mysql.connector.errors import Error
import os.path
import config

from mysql_connection import get_connection

class BankTranIdResource (Resource):
    def post(self):
        # 연결
        connection = get_connection()

        # 쿼리
        # DB에 저장된 가장 마지막 값을 가져옴
        query = '''select * from bank_tran_id
        order by created_at desc, num desc
        limit 1'''

        # 커서
        cursor = connection.cursor(dictionary = True)
        cursor.execute(query,)
        record_list = cursor.fetchall()

        current_dt = dt.datetime.now() # 현재 시간

        # 각 값의 연-월-일을 문자열로 반환
        if record_list != []:
            response = record_list[0]      # DB에서 가져온 값
            res_dt = response['created_at'].strftime('%Y%m%d')
        else:
            res_dt = '00010101'
        current_dt = current_dt.strftime('%Y%m%d')
        
        
        # 두 날짜가 같을 때
        if res_dt == current_dt :
            # num값이 없다면 0으로 지정
            if response['num'] == None:
                num = 0

            # num 값을 가져옴
            else:
                # num 값 1 증가
                num = response['num']+1 


        # 두 날짜가 다르다면 0으로 지정
        else:
            num = 0

        # DB와 통신
        try:
            # connection = get_connection()
            query = '''insert into bank_tran_id
            (num)
            values
            (%s)'''
            
            record = (num,)

            # 커서 연결 및 실행
            cursor = connection.cursor()    # 커서 가져오기
            cursor.execute(query, record)   # 커서 실행
            connection.commit()             # 반영

        except Error as err:
            return {'Error': str(err)}
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()

        num = str(num)              # 자릿수가 모자란만큼 앞에 '0'을 붙여줌
        if len(num) < 9:
            while (9-len(num)) != 0:
                num = '0'+num
        org_code = 'M202200391U'    # 기관 코드
        bank_tran_id = org_code+num # 거래 고유 번호 생성

        return bank_tran_id         # 거래 고유 번호 반환