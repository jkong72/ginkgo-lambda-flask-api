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
    print(data)
    if len(data) > 0 :
        df = pd.DataFrame(data)
        df['date'] = df['tran_datetime'].apply(lambda x: x[-2:])
        df_data = df.groupby('date')[['date','tran_amt']].sum()
        df_data.reset_index(drop=False, inplace=True)
        df_data['chart'] = 1
        fig = px.line(df_data, x='date', y='tran_amt', color='chart',  markers=True)

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

        # 범주 위치 조정
        # fig.update_layout(
        #     legend=dict(
        #         orientation="h",
        #         yanchor="bottom",
        #         y=1.02,
        #         xanchor="left",
        #         x=1
        #         ))
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left"
        ))
        chart1_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return chart1_json