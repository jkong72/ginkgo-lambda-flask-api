from typing import final
from xml.etree.ElementInclude import include
from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity


from mysql_connection import get_connection
from utils.url_request import url_binder, get_account, get_trade


# 계좌 정보 DB 통신문
class AccountInfoResource(Resource):
    # DB에서 계좌 정보 가져오기
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            user_id = get_jwt_identity    # 이용자 식별 (user_id)
            query = '''select tran_date, tran_time, branch_name, inout_type, tran_amt, account_id, type_id, memo
            from account
            where user_id = %s'''

            param = (user_id,)
            cursor = connection.cursor()
            cursor.execute(query, param)
            record_list = cursor.fetchall()

        except Error as err: # 예외처리 (에러)
            return {'Error':str(err)}
        finally:
            cursor.close()
            
        return {'data':'0'}

    # DB에 계좌 정보 쓰기 (오픈뱅킹에서 가져오기)
    @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self, user_seq_no):
        try: # 통신문
            connection = get_connection() # DB와 연결
            user_id = get_jwt_identity() # 이용자 식별 (user_id)

            result = get_account(user_seq_no) # 등록계좌조회

            for account in result['res_list']: # 계좌 정보 가져오기
                account_alias = account['account_alias']              #계좌 이름
                account_num_masked = account['account_num_masked']    #계좌 번호 (일부 가려짐)
                account_holder_name = account['account_holder_name']  #계좌주 이름
                bank_name = account['bank_name']                      #은행 이름
                fintech_use_num = account['fintech_use_num']          #핀테크 넘버
                account_type = account['account_type']                #계좌 유형 (1:수시입출금, 2:예적금, 6:수익증권, T:종합계좌)

                # query문
                # account 테이블에
                # 현재 유저id, 계좌 이름, 계좌 번호, 계좌주 이름, 은행 이름, 핀테크 번호, 계좌 유형을 저장
                query = '''insert into account
                (user_id, account_alias, account_num_masked, account_holder_name, bank_name, fintech_num, account_type)
                values
                (%s, %s, %s, %s, %s, %s, %s); '''

                param = (user_id, account_alias, account_num_masked, account_holder_name, bank_name, fintech_use_num)

                # 커서 연결 및 실행
                cursor = connection.cursor()    # 커서 가져오기
                cursor.execute(query, param)    # 커서 실행
                connection.commit()             # 반영

        except Error as err: # 예외처리
            return {'Error': str(err)}
        
        # 커서 및 연결 종료
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()


# 거래 내역 DB 통신문
class TradeInfoResource(Resource):
    # DB에서 거래 내역 가져오기
    @jwt_required() # 헤더를 통해 토큰을 받음
    def get(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            user_id = get_jwt_identity    # 이용자 식별 (user_id)
            query = '''select
                            tran_date, tran_time, print_content, inout_type, tran_amt, account_id, type_id, memo
                        from trade
                        where user_id = %s
                        order by tran_date, tran_time desc'''

            param = (user_id,)
            cursor = connection.cursor()
            cursor.execute(query, param)
            record_list = cursor.fetchall()

        except Error as err: # 예외처리 (에러)
            return {'Error':str(err)}
        finally:
            cursor.close()
            
        return {'data':'0'}

    # DB에 거래 내역 쓰기 (오픈뱅킹에서 가져오기)
    @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            user_id = get_jwt_identity() # 이용자 식별 (user_id)

            repeat == 'y'                       #실행을 위한 초기 값
            while repeat == 'y':                #다음 페이지가 있을 때만 실행
                result = get_trade()            # 등록계좌조회
                repeat = result['next_page_yn'] # 다음 페이지가 있는지 여부

                for trade in result['res_list']: # 거래정보 가져오기
                    tran_date = trade['tran_date']          # 거래일
                    tran_time = trade['tran_time']          # 거래시
                    inout_type = trade['inout_type']        # 입출금
                    print_content = trade['print_content']  # 통장인자
                    tran_amt = trade['tran_amt']            # 거래액

                    # query문
                    query = '''insert into trade
                    (user_id, trand_date, tran_time, inout_type, print_content, tran_amt)
                    values
                    (%s, %s, %s, %s, %s, %s)'''

                    param = (user_id, tran_date, tran_time, inout_type, print_content, tran_amt)

                    # 커서 연결 및 실행
                    cursor = connection.cursor()    # 커서 가져오기
                    cursor.execute(query, param)    # 커서 실행
                    connection.commit()               # 반영

        except Error as err: # 예외처리
            return {'Error': str(err)}

        # 커서 및 연결 종료
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()