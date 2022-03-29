import json
import plotly.graph_objects as go
import plotly
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from http import HTTPStatus
from mysql_connection import get_connection
from mysql.connector.errors import Error

# 두개의 데이트 타임은 다름으로 둘다 필요
from datetime import datetime as dt
import datetime
from dateutil.relativedelta import relativedelta




def main_chart():

    # db에서 유저 정보 받아오기
    # URL = "http://127.0.0.1:5000/main/info"
    # try :
    #     response = requests.get(URL)
    #     response = response.json()
    #     print(response)
    #     if response["error"] != 0 :
    #         return  {"error" : response["error"]}
    # except :
    #     return  {"error" : 4}
    
    # user_lnfo = response["user_lnfo"]
    # account_info = response["account_info"]
    # trade_info = response["trade_info"]
    # type_info = response["type_info"]

    user_id = 7
    try :
        print("db 커넥션 시작")
        connection = get_connection()
        print("db 커넥션 성공")


        # 먼저 유저정보부터 가져오기
        # 2. 쿼리문 
        query = '''SELECT id , expires_date, payday FROM ginkgo_db.user
                    where id = %s;
                    '''
        record = (user_id,)
        
        # 커넥션으로부터 커서를 가져온다.
        cursor = connection.cursor(dictionary = True)
        # 쿼리문을 커서에 넣어서 실행한다.
        cursor.execute(query, record)
        user_lnfo = cursor.fetchall()
        print(user_lnfo)


    except Error as e:
        print('Error ', e)
        # 6. email이 이미 DB에 있으면,
        #    이미 존재하는 회원이라고 클라이언트에 응답한다.
        return {'error' : 1} 
    try :
        # 계좌정보가져오기
        # 2. 쿼리문 
        query = '''SELECT * FROM account
                    where user_id = %s;
                    '''
        record = (user_id,)
        
        # 커넥션으로부터 커서를 가져온다.
        cursor = connection.cursor(dictionary = True)
        # 쿼리문을 커서에 넣어서 실행한다.
        cursor.execute(query, record)
        account_lnfo = cursor.fetchall()
        print(account_lnfo)

    except Error as e:
        print('Error ', e)
        # 6. email이 이미 DB에 있으면,
        #    이미 존재하는 회원이라고 클라이언트에 응답한다.
        return {'error' : 2} , HTTPStatus.BAD_REQUEST
    
    try :
        # 계좌정보가져오기
        # 2. 쿼리문 
        # 에러 빼고 일단 한다.
        query = '''SELECT td.id, td.user_id,td.tran_datetime, td.print_content, td.inout_type, td.tran_amt, td.account_id, tp.basic_type, tp.detail_type
                    FROM (SELECT * FROM trade where user_id = %s) td
                    left join type tp
                    on td.type_id = tp.id;
                    '''
        record = (user_id,)
        
        # 커넥션으로부터 커서를 가져온다.
        cursor = connection.cursor(dictionary = True)
        # 쿼리문을 커서에 넣어서 실행한다.
        cursor.execute(query, record)
        trade_lnfo = cursor.fetchall()

        i = 0
        for record in trade_lnfo:
            
            trade_lnfo[i]['tran_datetime'] = record['tran_datetime'].isoformat()         
            i = i + 1
        

        print(trade_lnfo)

    except Error as e:
        print('Error ', e)
        # 6. email이 이미 DB에 있으면,
        #    이미 존재하는 회원이라고 클라이언트에 응답한다.
        return {'error' :3} , HTTPStatus.BAD_REQUEST

    try :
        # 계좌정보가져오기
        # 2. 쿼리문 
        query = '''SELECT * FROM type
                    order by id; '''
        
        # 커넥션으로부터 커서를 가져온다.
        cursor = connection.cursor(dictionary = True)
        # 쿼리문을 커서에 넣어서 실행한다.
        cursor.execute(query, )
        type_lnfo = cursor.fetchall()
        print(type_lnfo)

    except Error as e:
        print('Error ', e)
        # 6. email이 이미 DB에 있으면,
        #    이미 존재하는 회원이라고 클라이언트에 응답한다.
        return {'error' : '1'} , HTTPStatus.BAD_REQUEST



    finally :
        if connection.is_connected():
            cursor.close()
            connection.close()
            print('MySQL connection is closed')




    # 차트 만들 데이터 정리
    df = pd.DataFrame(trade_lnfo)
    values_dict = df.groupby('detail_type')['tran_amt'].sum().to_dict()
    
    # 차트에 넣을 라벨과 부모라벨을 리스트에 담는 과정
    # 사용자가 쓴 타입의 라벨 == labels_list, 그 라벨의 부모(basic_type) 은 parents_list
    labels_list = list(values_dict.keys())
    type_df = pd.DataFrame(type_lnfo)

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
    
    user_name = account_lnfo[0]['account_holder_name']

    payday = user_lnfo[0]['payday']
    
    today = datetime.date(2022, 1, 31)

    if payday is not None :
        year = today.year
        month = today.month
        day = today.day

        
        if day - payday > 0 :
            get_data_to = str(year)+"-"+ str(month)+"-"+  str(day)
            get_data_to = datetime.date.fromisoformat(get_data_to)
            if month == 1 :
                get_data_from = str(year)+"-"+ str(12)+"-"+  str(day)
                get_data_from = datetime.date.fromisoformat(get_data_from)
            else : 
                get_data_from = str(year)+"-"+ str(month-1)+"-"+  str(day)
                get_data_from = datetime.date.fromisoformat(get_data_from)

        else : 
            if month == 1 :
                get_data_to = str(year)+"-"+ str(12)+"-"+  str(day)
                get_data_to = datetime.date.fromisoformat(get_data_to)
                get_data_from = str(year)+"-"+ str(11)+"-"+  str(day)
                get_data_from = datetime.date.fromisoformat(get_data_from)

            if month == 2 :
                get_data_to = str(year)+"-"+ str(1)+"-"+  str(day)
                get_data_to = datetime.date.fromisoformat(get_data_to)
                get_data_from = str(year)+"-"+ str(12)+"-"+  str(day)
                get_data_from = datetime.date.fromisoformat(get_data_from)

            else : 
                get_data_to = str(year)+"-"+ str(month-1)+"-"+  str(day)
                get_data_to = datetime.date.fromisoformat(get_data_to)
                get_data_from = str(year)+"-"+ str(month-1)+"-"+  str(day)
                get_data_from = datetime.date.fromisoformat(get_data_from)

            


        d_day = (today - datetime.date(2022, 1, 20)).days
        payday_ment = "월급까지 D-{}".format(d_day)
    else : 
         payday_ment = "월급일을 입력해주세요"

    return {"data" : result, "name" : user_name, "payday_ment" : payday_ment}
