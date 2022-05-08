# 상세 화면에서 보여줄 직선 그래프

import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import requests
import config
import json

def chart1(wealth_result):
    data = wealth_result["trade_lnfo"]
    print("chart1 data /////")
    # print(data)
    # 거래내역이 비어있지 않을때 
    if len(data) > 0 :
        # 거래내역으로 데이터 프레임제작
        df = pd.DataFrame(data)
        # 거래일별 소비금액 계산
        df_data = df.groupby('tran_datetime')[['tran_amt']].sum()
        # 소비금액이 0 인 날짜가 있다면 추가로 넣어주는 작업
        date_list = wealth_result["day_list"]
        set(df_data.index)
        set(date_list)
        blank_list = set(date_list)- set(df_data.index)
        blank_list
        for date in blank_list :
            df_data.loc[date] = [0]
        
        # 날짜 순서대로 정렬 후 마무리
        df_data = df_data.sort_index()
        df_data.reset_index(drop=False, inplace=True)

        # 시작날짜의 통장 잔액의 합계 week_money
        week_money = wealth_result["week_money"]
        # 빈 데이터 프레임 만들어서 0으로 채워넣기
        df2 = pd.DataFrame(index=range(0,7),columns=['tran_datetime', 'tran_amt'])
        df2 = df2.fillna(0)
        # week_money에서 일별 소비금액을 제해 일별 잔액 계산
        for i in range(7) :
            if i == 0 :
                df2.iloc[i, 0] = date_list[i]
                df2.iloc[i, 1] = week_money - df_data.iloc[i, 1]
            else :
                df2.iloc[i, 0] = date_list[i]
                df2.iloc[ i, 1] = df2.iloc[ i - 1 , 1] - df_data.iloc[i, 1]

        # 차트로 넘겨줄 데이터 정리
        chart1_x = df_data['tran_datetime'].tolist()
        chart1_y = df_data['tran_amt'].tolist()
        chart2_x = df2['tran_datetime'].tolist()
        chart2_y = df2['tran_amt'].tolist()




        return {"chart1_x" : chart1_x, "chart1_y":chart1_y, "chart2_x":chart2_x,  "chart2_y":chart2_y}

