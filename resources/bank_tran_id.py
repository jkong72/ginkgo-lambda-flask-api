import requests
import datetime as dt
from flask_restful import Resource
from mysql.connector.errors import Error
import os.path
import config


from mysql_connection import get_connection

class BankTranIdResource (Resource):
    org_code = 'M202200391U'

    def get(self):
        # 가장 최신의 created_at을 가져옴
        try:
            connection = get_connection()

            query = '''select * from bank_tran_id
            order by created_at desc
            limit 1'''

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query,)
            record_list = cursor.fetchall()

            print (record_list)
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = record_list[i]['created_at'].strftime("%Y%m%d")
                i=i+1

        except Error as err:
            return {'Error':str(err)}
        finally:
            cursor.close()

        return {'data':record_list}

    def post(self):
        # 마지막 created_at 값을 가져옴
        # url = config.Config.END_POINT
        # url = url+'/bank_tran_id'
        # url = 'http://127.0.0.1:5000/bank_tran_id'
        # res = requests.get(url)
        # print('-'*15)
        # print(res.json)
        # print('-'*15)
        # res_dt = res.json['created_at']
        connection = get_connection()

        query = '''select * from bank_tran_id
        order by created_at desc
        limit 1'''

        cursor = connection.cursor(dictionary = True)
        cursor.execute(query,)
        record_list = cursor.fetchall()


        
        current_dt = dt.datetime.now()
        response = record_list[0]

        # 각 값의 연-월-일을 문자열로 반환
        res_dt = response['created_at'].strftime('%Y%m%d')
        current_dt = current_dt.strftime('%Y%m%d')
        
        
        # 두 날짜가 같을 때
        if res_dt == current_dt :
            # num값이 없다면 0으로 지정
            if response['num'] == None:
                num = 0

            ## num 값을 가져옴
            else:
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
            cursor.execute(query, record)    # 커서 실행
            connection.commit()             # 반영

            print(num)

        except Error as err:
            return {'Error': str(err)}
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()

    

#     # 숫자의 자릿수를 맞춤
#     num_code = str(num)                     # 문자열로 변환
#     if len(num_code) < 9:                   # 자릿수가 9자리 이하일때
#         while (9-len(num_code)) == 0:       # 9자리가 될 때까지
#             num_code = '0'+num_code         # 앞자리에 '0' 붙임

#     tran_id_num = org_code+num_code

# # 거래 고유 번호 생성기
# def auto_increment_num():

#     path = 'date_checker.txt'   # 날짜 정보 경로
#     current_day = str(dt.datetime.now().day) # 현재 날짜 (스트링)

#     if os.path.isfile(path):     # 날짜 파일 있음
        
#         saved_file = open('date_checker.txt', 'r') # 기록된 날짜 확인
#         saved_day = saved_file.read()
#         saved_file.close()

#         if saved_day == current_day: # 두 날짜가 일치하면
#             num = num+1                     # 숫자를 증가
#             return int(num)

#         else:                        # 두 날짜가 다르면 (날짜의 갱신 있음)
#             saved_file = open('date_checker.txt', 'w')
#             saved_file.write(dt.datetime.now().strftime('%d')) # 현재 날짜를 덮어 씌우고
#             num = 0                                            # 숫자는 0으로 설정
#             saved_file.close()
#             return int(num)

#     else: # 날짜 파일 없음
#         date_check = open('date_checker.txt', 'w')
#         date_check.write(dt.datetime.now().strftime('%d')) # 현재 날짜를 덮어 씌우고
#         num = 0                                            # 숫자를 0으로 설정
#         date_check.close()
#         return int(num)
    

# def auto_inc_code ():

#     org_code = 'M202200391U'

#     auto_increment = str(num)      # 문자열로 변환
#     if len(auto_increment) < 9:    # 자릿수가 9자리 이하일때
#         while (9-len(auto_increment)) == 0: # 9자리가 될 때까지
#             auto_increment = '0'+auto_increment        # 앞자리에 '0' 붙임

#     return org_code+auto_increment # 거래 고유 번호 반환