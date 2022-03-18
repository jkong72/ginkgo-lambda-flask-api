from xml.etree.ElementInclude import include
from flask_restful import Resource
from flask import request
from http import HTTPStatus
from mysql.connector.errors import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import requests

from utils.url_path import url_binder


# 등록 계좌 조회 (핀테크 얻기 위함)
def get_account (user_seq_no):
    base_url = 'https://testapi.openbanking.or.kr/v2.0/account/list?'
    user_seq_no = 'user_seq_no={}'.format(user_seq_no)
    include_cancel_yn = 'include_cancel_yn=N'
    sort_order = 'sort_order=D'

    url_list = [base_url, user_seq_no, include_cancel_yn, sort_order]
    url = url_binder(url_list) # url의 파라미터를 엮어서 url을 완성하는 함수

    account_result = requests.get(url)
    return account_result

# 등록 계좌에서 핀테크 가져오는 부분 (분리해야함)
result = get_account()
result['res_cnt']                   #계좌 개수
for account in result['res_list']:
    account['account_alias']        #계좌 이름
    account['account_num_masked']   #계좌 번호 (일부 가려짐)
    account['account_holder_name']  #계좌주 이름
    account['bank_name']            #은행 이름
    account['fintech_use_num']      #핀테크 넘버
    account['account_type']         #계좌 유형 (1:수시입출금, 2:예적금, 6:수익증권, T:종합계좌)

# 거래 내역 조회
def get_trade (fintech_num):
    today_date = dt.today() # 현재 날짜
    back_date = today_date - relativedelta(years=2)
    today_date = today_date.strftime('%y%m%d')
    back_date = back_date.strftime('%y%m%d')

    base_url = 'https://testapi.openbanking.or.kr/v2.0/account/transaction_list/fin_num?' # 기본 URL
    inquiry_base = 'inquiry_base=D&'                                   # 조회 기준 (D:일간, T: 시간)
    sort_order = 'sort_order=D&'                                       # 정렬 순서
    inquiry_type = 'inquiry_type=A&'                                   # 조회 구분 (A: 모두, I: 입금, O: 출금)
    bank_tran_id = 'bank_tran_id=M202200391U{}'.format()               # 은행 거래 고유번호(매일 순차 증가)
    fintech_use_num = 'fintech_use_num={}'.format(fintech_num)         # 핀테크 번호
    from_date = 'from_date={}'.format(today_date)                      # 조회시작일.
    to_date = 'to_date={}'.format(back_date)                           # 조회종료일
    befor_inquiry_trace_info = 'befor_inquiry_trace_info={}'.format()  # 페이지(0~19)
    tran_dtime = 'tran_dtime={}'.format(today_date)                    # 요청 일시 (오늘 날짜)

    url_list = [base_url, inquiry_type, inquiry_base, sort_order, bank_tran_id, fintech_use_num, from_date, to_date, befor_inquiry_trace_info, tran_dtime]
    url = url_binder(url_list)

    trade_result = requests.get(url)
    return trade_result

# 거래 내역 조회에서 정보 가져오는 부분 (분리해야함)
repeat = 'y'             # 값이 실행될 수 있게 설정
while repeat == 'y':     # 다음 페이지가 있다면 반복
    result = get_trade()
    repeat = result['next_page_yn'] # 다음 페이지 여부
    for trade in result['res_list']:
        trade['tran_date']          # 거래일
        trade['tran_time']          # 거래시
        trade['inout_type']         # 입출금
        trade['print_content']      # 통장인자
        trade['tran_amt']           # 거래액
