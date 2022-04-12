import pandas as pd
import plotly
import plotly.express as px
import datetime
from dateutil.relativedelta import relativedelta
import requests
import config
import json

def chart1(wealth_result):
    data = wealth_result["trade_lnfo"]
    print("chart1 data /////")
    # print(data)
    if len(data) > 0 :
        df = pd.DataFrame(data)
        df_data = df.groupby('tran_datetime')[['tran_amt']].sum()
        date_list = [25,26,27,28,29,30, 31]
        set(df_data.index)
        set(date_list)
        blank_list = set(date_list)- set(df_data.index)
        blank_list
        for date in blank_list :
            df_data.loc[date] = [0]
        df_data = df_data.sort_index()
        df_data.reset_index(drop=False, inplace=True)
        df_data['chart'] = 1    

        week_money = wealth_result["week_money"]
        df2 = pd.DataFrame(index=range(0,7),columns=['tran_datetime', 'tran_amt', 'chart'])
        df2 = df2.fillna(0)
        for i in range(7) :
            if i == 0 :
                df2.iloc[i, 0] = date_list[i]
                df2.iloc[i, 1] = week_money - df_data.iloc[i, 1]
            else :
                df2.iloc[i, 0] = date_list[i]
                df2.iloc[ i, 1] = df2.iloc[ i - 1 , 1] - df_data.iloc[i, 1]
        df2['chart'] = 2
        df_chart = pd.concat([df_data, df2]) 

        fig = px.line(df_chart, x='tran_datetime', y='tran_amt', color='chart',  markers=True)

        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left"
        ))
        chart1_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return chart1_json
    else :
        df = px.data.gapminder().query("continent == 'Oceania'")
        fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)

        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left"
        ))
        chart1_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return chart1_json