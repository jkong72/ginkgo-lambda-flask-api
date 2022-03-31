from flask_restful import Resource
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import config
import datetime as dt

from mysql_connection import get_connection
from utils.openbaking_req import url_binder, get_account, get_trade

rep_ok = 0
rep_err = 1

# 계좌 정보 DB 통신문
class AccountInfoResource(Resource):
    # DB에서 계좌 정보 가져오기
    # @jwt_required() # 헤더를 통해 토큰을 받음
    def get(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            # user_id = get_jwt_identity    # 이용자 식별 (user_id) # todo
            user_id = 1    # 이용자 식별 (user_id) # todo
            query = '''select account_alias, account_num_masked, account_holder_name, bank_name, fintech_num, account_type
            from account
            where user_id = %s'''

            param = (user_id,)
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

        except Error as err: # 예외처리 (에러)
            return {'error':rep_err}
        finally:
            cursor.close()
            
        return {'data':record_list}

    # DB에 계좌 정보 쓰기 (오픈뱅킹에서 가져오기)
    # @jwt_required() # 헤더를 통해 토큰을 받음
    def post(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            # user_id = get_jwt_identity() # 이용자 식별 (user_id)
            user_id = 1

            # requests.get()# 이용자 정보 # todo
            user_seq_no = '0' #user_seq_no 입력 #todo
            user_seq_no = config.Config.USER_SEQ_NO
            access_token = '0' # todo
            access_token = config.Config.ACCESS_TOKEN

            result = get_account(user_seq_no, access_token) # 등록계좌조회

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

                param = (user_id, account_alias, account_num_masked, account_holder_name, bank_name, fintech_use_num, account_type)

                # 커서 연결 및 실행
                cursor = connection.cursor()    # 커서 가져오기
                cursor.execute(query, param)    # 커서 실행
                connection.commit()             # 반영

        except Error as err: # 예외처리
            return {'error': rep_err}
        
        # 커서 및 연결 종료
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
        
        return { 'error' : rep_ok }


# 거래 내역 DB 통신문
class TradeInfoResource(Resource):
    # DB에서 거래 내역 가져오기
    # @jwt_required() # 헤더를 통해 토큰을 받음
    def get(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            # user_id = get_jwt_identity    # 이용자 식별 (user_id)
            user_id = 1    # 이용자 식별 (user_id)

            query = '''select
                            tran_datetime, print_content, inout_type, tran_amt, account_id, type_id
                        from trade
                        where user_id = %s
                        order by tran_datetime desc'''

            param = (user_id,)
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
            
            i = 0
            for record in record_list:
                record_list[i]['tran_datetime'] = record_list[i]['tran_datetime'].strftime("%Y%m%d")
                i=i+1


        except Error as err: # 예외처리 (에러)
            return {'error':rep_err}
        finally:
            cursor.close()
            
        return {'data':record_list}

    # DB에 거래 내역 쓰기 (오픈뱅킹에서 가져오기)
    # @jwt_required() # 헤더를 통해 토큰을 받음 # todo
    def post(self):
        try: # 통신문
            connection = get_connection() # DB와 연결
            # user_id = get_jwt_identity() # 이용자 식별 (user_id) # todo
            user_id = 1
            access_token = config.Config.ACCESS_TOKEN # todo

            end_point = config.Config.END_POINT
            end_point = config.Config.LOCAL_URL

            account_res = requests.get(end_point+'/account').json()

            # 추가된 코드 ///////////////////////////////////////////////////////////////////////////////////

            # 유저가 월급 관련 정보를 입력했는지 확인하는 코드
            try :
      
                query = '''SELECT id ,payday
                            FROM ginkgo_db.user
                            where id = %s;
                            '''
                record = (user_id,)
                
                # 커넥션으로부터 커서를 가져온다.
                cursor = connection.cursor(dictionary = True)
                # 쿼리문을 커서에 넣어서 실행한다.
                cursor.execute(query, record)
                record_list = cursor.fetchall()
                print(record_list)
                if record_list[0]['payday'] is None :
                    IsFirst = True
                else :
                    IsFirst = False
                
                print(IsFirst)

                
            except Error as e:
                print('Error ', e)
                return {'error' : rep_err}     

            # db 에서 classification_list 가져오는 코드
            try :
                query = """select  type_id, print_content
                            from classification_type
                            where user_id = %s;"""
                                        
                record = (user_id, )
                cursor = connection.cursor(dictionary = True)
                cursor.execute(query, record)
                # select 문은 아래 내용이 필요하다.
                # 커서로 부터 실행한 결과 전부를 받아와라.
                record_list = cursor.fetchall()
                print("classification_list 내역")
                print(record_list)
                classification_list = record_list
            except Error as e :
                print('Error while connecting to MySQL', e)
                return {'error' : rep_err}


            # db에서 키워드 가져오는 쿼리
            try :

                # 2. 해당 테이블, recipe 테이블에서 select
                query = """SELECT type_id, keyword
                            FROM type_keyword
                            order by type_id;"""
                                        
                cursor = connection.cursor(dictionary = True)
                cursor.execute(query, )
                # select 문은 아래 내용이 필요하다.
                # 커서로 부터 실행한 결과 전부를 받아와라.
                record_list = cursor.fetchall()
                print("keyword_list 내역")
                print(record_list)
                keyword_list = record_list
                
            except Error as e :
                # 뒤의 e는 에러를 찍어라 error를 e로 저장했으니까!
                print('Error while connecting to MySQL', e)
                return {'error' : rep_err}

 
            # 반복문의 시작
            for data in account_res['data']:
                fintech_num = data['fintech_num']

                page = 0

                repeat = 'Y'                       # 실행을 위한 초기 값
                while repeat == 'Y':               # 다음 페이지가 있을 때만 실행
                    bank_tran_id = requests.post(end_point+'/bank_tran_id').json()
                    result = get_trade(bank_tran_id, fintech_num, access_token, page)            # 등록계좌조회
                    repeat = result['next_page_yn'] # 다음 페이지가 있는지 여부
                    print(result['next_page_yn'])
                    page = page+1

                    # print (result['res_list'])
                    for trade in result['res_list']: # 거래정보 가져오기
                        tran_date = trade['tran_date']          # 거래일
                        tran_time = trade['tran_time']          # 거래시
                        inout_type = trade['inout_type']        # 입출금
                        print_content = trade['print_content']  # 통장인자
                        tran_amt = int(trade['tran_amt'])       # 거래액

                        tran_datetime = dt.datetime.strptime(tran_date+tran_time, '%Y%m%d%H%M%S')

                        # classification 테이블에 저장된 print_content 와 그  print_content 의  type_id를 각각 리스트에 저장
                        c_p_c = []
                        c_t_id = []
                        for dic in classification_list :
                            c_p_c.append(dic['print_content'])
                            c_t_id.append(dic['type_id'])

                        # type_keyword 테이블에 저장된 print_content 와 그  print_content 의  type_id를 각각 리스트에 저장
                        keyword_word_list = []
                        keyword_t_id = []
                        for dic in keyword_list :
                            keyword_word_list.append(dic['keyword'])
                            keyword_t_id.append(dic['type_id'])
                        
                        type_id = "n"

                        # classification테이블에 저장된 print_content가 있으면 그 print_content의 type_id를 type_id로 저장
                        if print_content in c_p_c :
                            type_id = c_t_id[c_p_c.index(print_content)]
                        # 그게 아니라면 키워드 리스트에 있는지 확인
                        else :
                            for word in keyword_word_list:
                                if word in print_content:
                                    type_id = keyword_t_id[keyword_word_list.index(word)]


                                
                        # 만약 classification테이블에 저장된 print_content도 아니고 키워드 리스트에도 해당되지않는다면 type_id 는 기타로 지정
                        if type_id == "n" :
                            type_id = 8

                                    
                        

                        account_id = 1 # 계좌 id값 # todo

                        # query문
                        query = '''insert into trade
                        (user_id, tran_datetime, print_content, inout_type, tran_amt, account_id, type_id)
                        values
                        (%s, %s, %s, %s, %s, %s, %s)'''

                        param = (user_id, tran_datetime, print_content, inout_type, tran_amt, account_id, type_id)

                        # 커서 연결 및 실행
                        cursor = connection.cursor()    # 커서 가져오기
                        cursor.execute(query, param)    # 커서 실행
                        connection.commit()               # 반영




            
        except Error as err: # 예외처리
            return {'Error': rep_err}

        # 커서 및 연결 종료
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()

        return { 'error' : rep_ok }