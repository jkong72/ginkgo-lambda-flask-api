import json
import plotly.graph_objects as go
import plotly
import pandas as pd
import requests
from http import HTTPStatus
from mysql_connection import get_connection
from mysql.connector.errors import Error


import datetime
from dateutil.relativedelta import relativedelta




def main_chart():
    # 개발 임시 날짜 지정
    today = datetime.date(2021, 12, 31)
    get_data_from = today + relativedelta(months=-1)
    get_data_from = get_data_from.isoformat()
    get_data_to = today + relativedelta(days=+1)
    get_data_to = get_data_to.isoformat()
    
    print(get_data_from)
    print(get_data_to)


    user_id = 1

    
    # db에서 유저 정보 받아오기
    URL = "http://127.0.0.1:5000/main/info"
    try :
        print("get main info start")
        response = requests.get(URL)
        response = response.json()
        print("get main info end")
        print(response)

        if response["error"] == 8282 :
            try :
                get_url =  "http://127.0.0.1:5000/trade"
                print("get openBanking Trade info start")
                response = requests.post(get_url)
                response = response.json()
                print("get openBanking Trade info end")
            except :
                return  {"error" : 4444}
            # todo 이거 페이지 재 로드하거나 .. 함수 처음부터 다시 시작하는거 어떻게 하지?
            if response["result"] == 0 :
                try :
                    print("get main info start")
                    response = requests.get(URL)
                    response = response.json()
                    print("get main info end")
                    print(response)
                except :
                    return  {"error" : 54}

        elif response["error"] != 0 :
            return  {"error" : response["error"]}

    except :
        return  {"error" : 54}
    
    user_lnfo = response["user_info"]
    account_info = response["account_info"]
    trade_info = response["trade_info"]
    type_info = response["type_info"]

   
  


    # 차트 만들 데이터 정리
    df = pd.DataFrame(trade_info)
    userChart2 = False

    # 나중에 보낼 지출 총액, 수입 총액
    money_dict = {}
    money_dict["income"] = df.loc[df['inout_type']=='입금', 'tran_amt'].sum()
    money_dict["outcome"] = df.loc[df['inout_type']=='출금', 'tran_amt'].sum()

    if money_dict["income"] - money_dict["outcome"] < 0 :
        userChart2 = True

    values_dict = df.groupby('detail_type')['tran_amt'].sum().to_dict()
    
    
    # 차트에 넣을 라벨과 부모라벨을 리스트에 담는 과정
    # 사용자가 쓴 타입의 라벨 == labels_list, 그 라벨의 부모(basic_type) 은 parents_list
    labels_list = list(values_dict.keys())
    if '급여' in labels_list :
        userChart2 == True
    type_df = pd.DataFrame(type_info)

    if userChart2 == False :

        # 디테일 타입으로부터 베이식 타입 추출을 위한 딕셔너리
        set_type_dic = type_df[['basic_type', 'detail_type']].set_index('detail_type').to_dict('index')
        
        # 1차 디테일 타입으로부터 베이식 타입 추출
        parents_list = []
        for label in labels_list :
            parents_list.append(set_type_dic[label]['basic_type'])

        # 2차 다듬기 베이식 분류는 부모를 급여로, 급여는 부모가 없는 것으로 수정
        for i in range(len(labels_list)):
            if labels_list[i] != '급여':
                if labels_list[i] == parents_list[i]:
                    parents_list[i] = '급여'                                               
            else :
                parents_list[i] = ''

        
        # 사용자가 라벨별로 쓴금액 값 리스트에 담기
        values_list = list(values_dict.values())

        # parents_list 에는 있는데 라벨에 없는경우 추가해주는 코드
        complement = list(set(parents_list) - set(labels_list))

        complement.remove('')
        print(complement)
        for label in complement :
            labels_list.append(label)
            parents_list.append('급여')
            values_list.append(int(df.loc[df['basic_type'] == label, 'tran_amt'].sum()))


        print(labels_list)
        print(parents_list)
        print(values_list)


    if userChart2 == True :
         # 디테일 타입으로부터 베이식 타입 추출을 위한 딕셔너리
        set_type_dic = type_df[['basic_type', 'detail_type']].set_index('detail_type').to_dict('index')
        
        # 1차 디테일 타입으로부터 베이식 타입 추출
        parents_list = []
        for label in labels_list :
            parents_list.append(set_type_dic[label]['basic_type'])

        # 2차 다듬기 베이식 분류는 부모를 총지출로
        for i in range(len(labels_list)):
            if labels_list[i] != '총지출':
                if labels_list[i] == parents_list[i]:
                    parents_list[i] = '총지출'       

        # 사용자가 라벨별로 쓴금액 값 리스트에 담기
        values_list = list(values_dict.values())   

        # parents_list 에는 있는데 라벨에 없는경우 추가해주는 코드
        complement = list(set(parents_list) - set(labels_list))   
        complement.remove('총지출')

        for label in complement :
            labels_list.append(label)
            parents_list.append('총지출')
            values_list.append(int(df.loc[df['basic_type'] == label, 'tran_amt'].sum()))
        
        print(labels_list)
        print(parents_list)
        print(values_list)

        # 마지막으로 급여대신 총 지출을 리스트에 집어넣는 과정
        labels_list.append('총지출')
        parents_list.append('')
        values_list.append(money_dict["outcome"])

        

    # 차트 만들어서 json형태로 넘겨주주기
    fig =go.Figure(go.Sunburst(
    labels=labels_list,
    parents=parents_list,
    values=values_list,
    branchvalues="total"
    ))
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0), height=800)
    result = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    # 유저 이름 뽑아내기
    user_name = account_info[0]['account_holder_name']


    # 계좌 정보에서 핀테크 번호로 잔액조회 돌리기
    # 기존 current_time = datetime.now() 에서 변경 ## 추후 today를 변경시 변경
    current_time = today
    current_time = current_time.strftime("%Y%m%d%H%M%S")
    print(current_time)
    print(type(current_time))
    i = 0
    amt_sum = 0
    for account in account_info :
        try :
            URL = "http://127.0.0.1:5000/bank_tran_id"
            print("requests bankTranId")
            bankTranId = requests.post(URL)
            bankTranId = bankTranId.json()
            print(bankTranId)
            print("I`m get bankTranId")
        except :
            print("I`m error of bankTranId")
            return {'error' : 44}

        OBURL = "https://testapi.openbanking.or.kr/v2.0/account/balance/fin_num"
        print(account["fintech_num"])
        params = {"bank_tran_id" : bankTranId, "tran_dtime": current_time, "fintech_use_num" : account["fintech_num"]}
        headers = {"Authorization" : "Bearer " + user_lnfo[0]["access_token"]}
        try :
            response = requests.get(OBURL, headers=headers, params=params)
            response = response.json()
            
            print(type(response))
            print(response)

            account_info[i]["balance_amt"] = response["balance_amt"]
            amt_sum = amt_sum + int(response["balance_amt"])

            i = i + 1
            
        except :
            return  {"error" : 4444}
    
    print(account_info)
    money_dict["amt_sum"] = amt_sum
    print(money_dict)
    





    # 월급일 기준으로 거래 데이터 가져올 기준 정하기
    payday = user_lnfo[0]['payday']

    if payday is not None :
        year = today.year
        month = today.month
        day = today.day

        
        if day - payday < 0 :
            d_day =  day - payday
        
        else :
            next_payday = datetime.date(year, month, payday) + relativedelta(months=+1)
            d_day = (next_payday - today).days

        payday_ment = "월급까지 D-{}".format(d_day)

    else : 
         payday_ment = "월급일을 입력해주세요"




    # data = 차트.json
    return {"data" : result, "name" : user_name, "payday_ment" : payday_ment, 'account_info' : account_info, "money_dict" : money_dict}
