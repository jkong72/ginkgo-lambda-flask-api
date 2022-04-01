import json
import pandas as pd
import plotly
import plotly.express as px

# accounts = ['계좌1', '계좌2', '계좌3', '계좌4', '계좌5']

def chart1():
    df = px.data.gapminder().query("continent == 'Oceania'")
    fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)

    chart1_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return chart1_json

#     fig.update_layout(annotations=annotations)z
# var = chart1()

# print (var)