from flask import request
import datetime as dt
import math
import requests
from config import *


def regular_trade_detector():
    
    url = Config.LOCAL_URL
    url = url+'/trade'
    jwt = request.cookies.get('jwt_access_token')
    # jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1MDE4MTc0MSwianRpIjoiMmFjOWI4NDMtYjYxNS00OGQ1LTlmYzQtODEyMDNjNGNiOTUyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ODMsIm5iZiI6MTY1MDE4MTc0MSwiZXhwIjoxNjUwMTgyNjQxfQ.1Fn_l5NSEkYFSuF3-4g5qAXzmS1gUVIhaON1rxXm1WE"
    headers = {"Authorization":"Bearer "+jwt}
    trade_datas = requests.get(url=url, headers=headers).json() # 모든 거래내역
    # print (trade_datas)
    trade_datas = trade_datas['data'] # 사용할 데이터 파싱

    # 포함된 통장 인자
    print_content_list = set() # 모든 통장인자(빈 세트)
    trade_dict = {}
    for trade_data in trade_datas:
        print_content_list.add(trade_data['print_content']) # 모든 통장인자를 세트에 삽입 (중복방지)
        trade_dict[trade_data['print_content']] = []        # 각 통장인자를 키로 하는 빈 리스트 생성
        trade_dict[trade_data['print_content']+'amt'] = []  # 각 통장인자amt를 키로 하는 빈 리스트 생성
        trade_dict[trade_data['print_content']+'io'] = []   # 각 통장인자io를 키로 하는 빈 리스트 생성

    # 각 '통장인자'를 키로 하는 거래일시 딕셔너리 밸류
    for trade_data in trade_datas:
        trade_dict[trade_data['print_content']].append(trade_data['tran_datetime'])

    # 각 '통장인자amt'를 키로 하는 거래액수 딕셔너리 밸류
    for trade_data in trade_datas:
        trade_dict[trade_data['print_content']+'amt'].append(trade_data['tran_amt'])

    # 각 '통장인자io'를 키로 하는 입출금 딕셔너리 밸류
    for trade_data in trade_datas:
        trade_dict[trade_data['print_content']+'io'].append(trade_data['inout_type'])

    # 통장인자 세트 -> 리스트 형변환
    print_content_list = list(print_content_list)

    result = [] # 결과값을 담기 위한 비어있는 리스트
    for print_content in print_content_list: # 각 통장인자 별로 반복문 수행
        date_gap_list = [] # 거래일시 간격을 받을 리스트 (통장인자 별)
        if len(trade_dict[print_content]) > 3: # 최소 3번이상 결제된 데이터에 한하여

            for tran_date in trade_dict[print_content]: # 통장인자의 거래일시 가져옴
                date = dt.datetime.strptime(tran_date, '%Y%m%d')
                next_date_index = trade_dict[print_content].index(tran_date)+1 # 불러온 위치에서 다음 위치까지의 거리

                if len(trade_dict[print_content]) == next_date_index:
                    # 인덱스 범위가 초과되면 종료
                    pass
                else:
                    next_date = trade_dict[print_content][next_date_index] #저번 거래를 가져옴
                    next_date = dt.datetime.strptime(next_date,'%Y%m%d')
                    date_gap = date-next_date # 이번 거래와 저번 거래 사이의 차이 확인
                    # print('date_gap = '+str(date_gap))
                    if date_gap.days < 7:
                        # 날짜의 중복. 하루에 여러번 계산 되었다는 뜻으로, 발견되면 고정 거래에서 제외.
                        pass
                    else:
                        date_gap_list.append(date_gap.days)

            # 각 결제기간별 차이의 표준편차 계산
            vsum = 0
            for val in date_gap_list:
                mean = sum(date_gap_list) / len(date_gap_list) # 평균간격
                vsum = vsum + (val - mean)**2
                variance = vsum / len(date_gap_list)
                std = math.sqrt(variance) # 표준 편차
                print('std값'+str(std))

            # 통장인자별 거래액수 평균 계산
            avg_amt = sum(trade_dict[print_content+'amt'])
            avg_amt = avg_amt/len(trade_dict[print_content+'amt'])
            avg_amt = round(avg_amt)
            avg_amt = format(avg_amt, ',')

            iotype = trade_dict[print_content+'io']
            iotype = iotype[0]

            if std < 1.1:
                result.append([print_content, std, mean, avg_amt, iotype])

    return result