import datetime as dt
import math
import requests
# import config

def regular_trade_detector():
    # url = config.Config.LOCAL_URL
    # url = url+'/trade'
    url = 'http://127.0.0.1:5000/trade'
    trade_datas = requests.get(url).json()
    print (trade_datas)
    trade_datas = trade_datas['data'] # 사용할 데이터 파싱

    # 포함된 통장 인자
    print_content_list = set() # 모든 통장인자
    trade_dict = {}
    for trade_data in trade_datas:
        print_content_list.add(trade_data['print_content'])
        trade_dict[trade_data['print_content']] = []

    for trade_data in trade_datas:
        trade_dict[trade_data['print_content']].append(trade_data['tran_datetime'])

    # 리스트 형변환
    print_content_list = list(print_content_list)

    result = []
    for print_content in print_content_list:
        date_gap_list = [] # 데이트 차이를 받을 리스트 (통장인자 별)
        if len(trade_dict[print_content]) > 3: # 최소 3번이상 결제된 데이터에 한하여
            for tran_date in trade_dict[print_content]:
                date = dt.datetime.strptime(tran_date, '%Y%m%d')
                next_date_index = trade_dict[print_content].index(tran_date)+1 # 불러온 위치에서 다음 위치까지의 거리
                # print(len(trade_dict[print_content]))
                # print(next_date_index)
                if len(trade_dict[print_content]) == next_date_index: # 인덱스 범위가 초과되면 종료
                    # print('인덱스 초과')
                    pass
                else:
                    # print('계산')
                    next_date = trade_dict[print_content][next_date_index] #저번 거래를 가져옴
                    next_date = dt.datetime.strptime(next_date,'%Y%m%d')
                    # print (date)
                    # print (next_date)
                    date_gap = date-next_date # 이번 거래와 저번 거래 사이의 차이 확인
                    # print('date_gap = '+str(date_gap))
                    if date_gap.days < 7:
                        # 날짜의 중복. 하루에 여러번 계산 되었다는 뜻으로, 발견되면 고정 거래에서 제외.
                        # print('날짜 중복')
                        pass
                    else:
                        date_gap_list.append(date_gap.days)

            # 각 결제기간별 차이의 표준편차 계산
            vsum = 0
            for val in date_gap_list:
                mean = sum(date_gap_list) / len(date_gap_list)
                vsum = vsum + (val - mean)**2
                variance = vsum / len(date_gap_list)
                std = math.sqrt(variance)

            result.append([print_content, std])

    return result

print (regular_trade_detector())