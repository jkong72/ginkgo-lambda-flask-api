import requests
import datetime as dt
from dateutil.relativedelta import relativedelta
import os.path
from config import Config


# 등록 계좌 조회 (핀테크 얻기 위함)
def get_account (user_seq_no, access_token):
    url = 'https://testapi.openbanking.or.kr/v2.0/account/list'
    params = {'user_seq_no':user_seq_no,
                'include_cancel_yn':'N',
                'sort_order':'D'}

    header = {'Authorization': 'Bearer '+access_token}

    account_result = requests.get(url=url, params=params, headers=header)
    return account_result.json()

# 거래 내역 조회
def get_trade (last_trade_date, bank_tran_id, fintech_num, access_token, page):

    current_dtime = dt.datetime.now() # 현재 날짜 (datetime)
    today_date = current_dtime.strftime('%Y%m%d') # 현재 날짜 (Date -> 문자열)
    # last_trade_date = last_trade_date.strftime('%Y%m%d') # 조회 시작일 (Date -> 문자열)
    tran_dtime = current_dtime.strftime('%Y%m%d%H%M%S') #오늘 날짜 (Datetime -> 문자열)

    # inquiry_type                    # 조회 구분 (A: 모두, I: 입금, O: 출금)
    # inquiry_base                    # 조회 기준 (D:일간, T: 시간)
    # sort_order                      # 정렬 순서
    # bank_tran_id                    # 은행 거래 고유번호(매일 순차 증가)
    # fintech_use_num                 # 핀테크 번호
    # from_date                       # 조회시작일 ()
    # to_date                         # 조회종료일 (조회일)
    # befor_inquiry_trace_info        # 페이지(0~19)
    # tran_dtime                      # 요청 일시 (오늘 날짜)
    url = 'https://testapi.openbanking.or.kr/v2.0/account/transaction_list/fin_num' # 기본 URL

    params = {'inquiry_type':'A',
                'inquiry_base':'D',
                'sort_order':'D',
                'bank_tran_id':bank_tran_id,
                'fintech_use_num':fintech_num,
                'from_date':last_trade_date,
                'to_date':today_date,
                'befor_inquiry_trace_info':page,
                'tran_dtime':tran_dtime}


    header = {'Authorization': 'Bearer '+access_token}

    trade_result = requests.get(url=url, params=params, headers=header).json()
    return trade_result