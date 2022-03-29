import json
import plotly.graph_objects as go
import plotly
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

def main_chart():

    # db에서 유저 정보 받아오기
    URL = "http://127.0.0.1:5000/main/info"
    try :
        response = requests.get(URL)
        response = response.json()
        print(response)
        if response["error"] != 0 :
            return  {"error" : response["error"]}
    except :
        return  {"error" : 4}
    
    user_lnfo = response["user_lnfo"]
    account_info = response["account_info"]
    trade_info = response["trade_info"]
    type_info = response["type_info"]

    # 차트 만들 데이터 정리
    df = pd.DataFrame(trade_info)
    values_dict = df.groupby('detail_type')['tran_amt'].sum().to_dict()
    
    # 차트에 넣을 라벨과 부모라벨을 리스트에 담는 과정
    # 사용자가 쓴 타입의 라벨 == labels_list, 그 라벨의 부모(basic_type) 은 parents_list
    labels_list = list(values_dict.keys())
    type_df = pd.DataFrame(type_info)

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

    fig =go.Figure(go.Sunburst(
    labels=labels_list,
    parents=parents_list,
    values=values_list,
    branchvalues="total"
    ))
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0), height=800)
    result = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    user_name = account_info[0]['account_holder_name']


    return {"data" : result, "name" : user_name}
