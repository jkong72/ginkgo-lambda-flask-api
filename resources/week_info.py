from flask import request, render_template, make_response
from flask.json import jsonify
from flask_restful import Resource
from http import HTTPStatus

from mysql_connection import get_connection
from mysql.connector.errors import Error

from flask_jwt_extended import jwt_required, get_jwt_identity

import datetime
from dateutil.relativedelta import relativedelta
import requests
import config

rep_ok = 0
rep_err = 1

class WeekInfoResource(Resource) :
    @jwt_required()  
    def get(self) :
        today = datetime.date(2021, 12, 31)
        get_data_from = today + relativedelta(days=-6)
        get_data_from = get_data_from.isoformat()
        get_data_to = today + relativedelta(days=+1)
        get_data_to = get_data_to.isoformat()

        print(get_data_from)
        print(get_data_to)
        end_point = config.Config.END_POINT
        end_point = config.Config.LOCAL_URL


        user_id = get_jwt_identity()

        try :
            print("db 커넥션 시작")
            connection = get_connection()
            print("db 커넥션 성공")

            query = '''SELECT * FROM trade
                    where user_id=%s and tran_datetime >%s AND tran_datetime < %s;
                    '''
            record = (user_id,  get_data_from, get_data_to)

            # 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor(dictionary = True)
            # 쿼리문을 커서에 넣어서 실행한다.
            cursor.execute(query, record)
            trade_lnfo = cursor.fetchall()

            i = 0
            for record in trade_lnfo:
                trade_lnfo[i]['tran_datetime'] = record['tran_datetime'].day      
                i = i + 1


        except Error as e:
            print('Error ', e)
            # 6. email이 이미 DB에 있으면,
            #    이미 존재하는 회원이라고 클라이언트에 응답한다.
            return {'error' :3} , HTTPStatus.BAD_REQUEST



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

            query = '''SELECT access_token 
                        FROM user
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
            return {'error' : 1} 


        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')


        
        # 기존 week_now = datetime.now() 에서 변경 ## 추후 today를 변경시 변경
        # 잔액을 계산할 시작날짜의 통장 시작금액 가져오기
        # 날짜 설정
        print("시작날짜의 잔액 조회")
        week_now =  today + relativedelta(days=-6)
        
        print("시작날짜!!!!")
        print(week_now)
        week_day = week_now.day
        week_day_str = week_now.strftime("%Y%m%d%H%M%S")
        # 잔액의 총합 : amt_sum
        amt_sum = 0
        # 계좌별 잔액의 총합 반복문으로 더해서 구하기
        for account in account_lnfo :
            # 먼저 bank_tran_id 발급받기
            try :
                URL = end_point + "/bank_tran_id"
                print("requests bankTranId")
                bankTranId = requests.post(URL)
                bankTranId = bankTranId.json()
                print(bankTranId)
                print("I`m get bankTranId")
            except :
                print("I`m error of bankTranId")
                return {'error' : 44}

            # 오픈뱅킹 잔액조회 api 파라미터 
            OBURL = "https://testapi.openbanking.or.kr/v2.0/account/balance/fin_num"
            print(account["fintech_num"])
            params = {"bank_tran_id" : bankTranId, "tran_dtime": week_day_str, "fintech_use_num" : account["fintech_num"]}
            headers = {"Authorization" : "Bearer " + user_lnfo[0]["access_token"]}

            # 오픈뱅킹 잔액조회 api 사용
            try :
                
                response = requests.get(OBURL, headers=headers, params=params)
                response = response.json()

                print(type(response))
                print(response)

                
                # 총합을 구하기 위해 잔액을 amt_sum에 더하기
                amt_sum = amt_sum + int(response["balance_amt"])


            except :
                return  {"error" : 4444}

        
        print("시작날짜 총계합산 끝남")
        print(week_day)
        print("총계")
        print(amt_sum)
        
        
        week_money = amt_sum


        # 일주일의 날자만 겟하는 함수
        from_date =  today + relativedelta(days=-6)
        day_list = []
        for day in range(7) :
            day_list.append(from_date.day)
            from_date = from_date  + relativedelta(days=1)





        print(week_money)
        print("trade_info")
        print(trade_lnfo)

        return {"error" : 0, "trade_lnfo" : trade_lnfo, "week_money" : week_money, "day_list" : day_list}