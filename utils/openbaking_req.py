import requests
import datetime as dt
from dateutil.relativedelta import relativedelta
import os.path


# url의 파라미터를 엮어서 url을 완성하는 함수
def url_binder (url_list):
    url = ''
    for word in url_list:
        url = url+word
        if url_list.index(word) != 0: # 첫번째가 아니라면 &로 이어줌
            url = url+'&'

    url = url.strip('&') # 맨 마지막에 붙은 & 제거
    return url


# 등록 계좌 조회 (핀테크 얻기 위함)
def get_account (user_seq_no, access_token):
    url = 'https://testapi.openbanking.or.kr/v2.0/account/list'
    params = {'user_seq_no':user_seq_no,
                'include_cancel_yn':'N',
                'sort_order':'D'}
    # user_seq_no = 'user_seq_no={}'.format(user_seq_no)
    # include_cancel_yn = 'include_cancel_yn=N'
    # sort_order = 'sort_order=D'

    # url_list = [base_url, user_seq_no, include_cancel_yn, sort_order]
    # url = url_binder(url_list) # url의 파라미터를 엮어서 url을 완성하는 함수

    header = {'Authorization': 'Bearer '+access_token}

    account_result = requests.get(url=url, params=params, headers=header)
    return account_result.json()

# 거래 내역 조회
def get_trade (bank_tran_id, fintech_num, access_token, page):
    current_dtime = dt.datetime.now() # 현재 날짜

    # 조회 시작일
    # 서비스DB에 데이터가 없다면 조회일로부터 2년 전 까지의 거래 데이터를 가져옴
    if
    # 이미 거래데이터가 있다면, 마지막 거래일로부터 오늘까지의 거래 데이터를 가져옴
    back_date = current_dtime - relativedelta(years=2)
    today_date = current_dtime.strftime('%Y%m%d') # todo 
    back_date = back_date.strftime('%Y%m%d')
    tran_dtime = current_dtime.strftime('%Y%m%d%H%M%S')

    base_url = 'https://testapi.openbanking.or.kr/v2.0/account/transaction_list/fin_num?' # 기본 URL
    inquiry_type = 'inquiry_type=A'                                # 조회 구분 (A: 모두, I: 입금, O: 출금)
    inquiry_base = 'inquiry_base=D'                                # 조회 기준 (D:일간, T: 시간)
    sort_order = 'sort_order=D'                                    # 정렬 순서
    bank_tran_id = 'bank_tran_id={}'.format(bank_tran_id)          # 은행 거래 고유번호(매일 순차 증가)
    fintech_use_num = 'fintech_use_num={}'.format(fintech_num)     # 핀테크 번호
    from_date = 'from_date={}'.format(back_date)                  # 조회시작일 ()
    to_date = 'to_date={}'.format(today_date)                       # 조회종료일 (조회일)
    befor_inquiry_trace_info = 'befor_inquiry_trace_info={}'.format(page)  # 페이지(0~19)
    tran_dtime = 'tran_dtime={}'.format(tran_dtime)                # 요청 일시 (오늘 날짜)

    url_list = [base_url, fintech_use_num, bank_tran_id, inquiry_type, inquiry_base, from_date, to_date, sort_order, tran_dtime, befor_inquiry_trace_info]
    url = url_binder(url_list)

    header = {'Authorization': 'Bearer '+access_token}

    trade_result = requests.get(url=url, headers=header).json()
    return trade_result