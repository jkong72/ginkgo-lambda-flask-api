import json
import pandas as pd
import plotly
import plotly.express as px

# accounts = ['계좌1', '계좌2', '계좌3', '계좌4', '계좌5']




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

#     fig.update_layout(annotations=annotations)z
# var = chart1()

# print (var)