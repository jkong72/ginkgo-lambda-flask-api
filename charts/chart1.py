import json
import pandas as pd
import plotly
import plotly.express as px

# accounts = ['계좌1', '계좌2', '계좌3', '계좌4', '계좌5']

<<<<<<< HEAD


    df = px.data.gapminder().query("continent == 'Oceania'")
    fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)

=======
def chart1(headers):

    # 유저의 1주일 정보 
    URL = config.Config.LOCAL_URL + '/week_info'
    response = requests.get(URL)
    #  {"error" : 0, "trade_lnfo" : trade_lnfo, "week_money" : week_money}
    data = response["trade_lnfo"]
    df = pd.DataFrame(data)
    df['date'] = df['tran_datetime'].apply(lambda x: x[-2:])
    df_data = df.groupby('date')[['date','tran_amt']].sum()
    df_data.reset_index(drop=False, inplace=True)
    df_data['chart'] = 1
    fig = px.line(df_data, x='date', y='tran_amt', color='chart',  markers=True)

>>>>>>> parent of ceb8dad (Merge branch 'main' into chart_data_hhh)
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

#     fig.update_layout(annotations=annotations)z
# var = chart1()

# print (var)