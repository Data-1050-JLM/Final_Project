import dash
from dash import dash_table
from dash import dcc # dash core components
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import requests
import sympy
import plotly.express as px
import plotly.graph_objs as go
from data_manipulation import import_data
from weather_visuals import icons
import calendar

#live, aqi_hist, weather_pred = import_data()
live, aqi_hist, weather_pred = import_data()

def page_header():
    """
    Returns the page header as a dash `html.Div`
    """
    return html.Div(id='header', children=[
        html.Div([html.H3('Visualization with datashader and Plotly')],
                 className="ten columns"),
        html.A([html.Img(id='logo', src=app.get_asset_url('github.png'),
                         style={'height': '35px', 'paddingTop': '7%'}),
                html.Span('Blownhither', style={'fontSize': '2rem', 'height': '35px', 'bottom': 0,
                                                'paddingLeft': '4px', 'color': '#a3a7b0',
                                                'textDecoration': 'none'})],
               className="two columns row",
               href='https://github.com/blownhither/'), #change this as it references personal git page
    ], className="row")

def description():
    """
    Returns overall project description in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        Place Description Here. 
        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

app = dash.Dash(__name__)

app.layout = html.Div([
        html.P("Weather and Pollution Analysis in the United States by State:"),
        dcc.Dropdown(
        id='states', 
        options=[{'value': x, 'label': x} 
                 for x in live['state']],
        value="Rhode Island"),
        dcc.Graph(id='gen_metrics_temp', style={'height':'30%','width': '33%','display': 'inline-block'} ),
        dcc.Graph(id='gen_metrics_feels', style={'height':'30%','width': '33%','display': 'inline-block'} ),
        dash.html.Img(id='gen_metrics_icons', style={'height':'30%','width': '20%','display': 'inline-block',  
        'padding-top': '50px','padding-bottom': '50px' } ),
        dcc.Graph(id="USA_MAP",style={'width': '50%','display': 'inline-block'}),
        dcc.Graph(id="bar_line", style={'width': '50%','display': 'inline-block'}),

        dcc.Graph(id="Weahter_forecast", style={'width': '40%'}),
        dcc.Tabs([
        dcc.Tab(label='pm2.5', children=[
            dcc.Graph(id='heatmap1', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'}),
        dcc.Tab(label='o3', children=[
            dcc.Graph(id='heatmap2', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'}),
        dcc.Tab(label='pm10', children=[
            dcc.Graph(id='heatmap3', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'}),
         dcc.Tab(label='no2', children=[
            dcc.Graph(id='heatmap4', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'}),
         dcc.Tab(label='so2', children=[
            dcc.Graph(id='heatmap5', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'}),
         dcc.Tab(label='co', children=[
            dcc.Graph(id='heatmap6', style={'width': '50%','display': 'inline-block'})
        ],style={'width': '5%','display': 'inline-block'})], style={'display': 'inline-block'})
      
])

@app.callback(
    Output("USA_MAP", "figure"), 
    Input("states", "value"),)
def display_choropleth(df):
    df = live
    fig = px.choropleth(df, color="Temperature", locations="STATE", locationmode="USA-states", scope="usa")
    fig.update_layout(title={'text':'Current Temperature by State',
    'xanchor':'center',
    'yanchor':'top',
    'x':0.5})

    return fig

@app.callback(
    Output("bar_line", "figure"), 
    [Input("states", "value")])
def display_graph(states):
    df = live[live['state'].eq(states)]


    bar_graph = go.Bar(x=df['graph_date'],
                    y=df['pm2.5'],
                    name='pm2.5',
                    yaxis='y1'
                    )
    line_graph = go.Line(x=df['graph_date'],
                        y=df['Temperature'],
                        name='Temperature (°F)',
                        mode='lines+markers',
                        yaxis='y2')

    data = [line_graph, bar_graph]

    layout = go.Layout(title={'text': '{state}\'s Hourly Temperature and Pollution'.format(state=states),
         'y':0.9, # new
         'x':0.5,
         'xanchor': 'center',
         'yanchor': 'top' # new
        },
                       yaxis=dict(title='pm2.5',
                                   side='right'),
                       yaxis2=dict(title='Temperature (°F)',
                                   overlaying='y',
                                   side='left'))

    return go.Figure(data=data, layout=layout)


@app.callback(
    Output("Weahter_forecast", "figure"), 
    [Input("states", "value")])
def weather_pre(states):
    df = weather_pred[weather_pred['state'].eq(states)]
    fig = px.line(
        x = df['date_time'],
        y = df['Temperature'],
        #error_y = df['Maximum Temperature']
        #error_y_minus= df['Minimum Temperature']
    )
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Temperture (°F)')
    fig.update_layout(title={'text':'{state}\'s Temperature Forecast'.format(state=states),
    'xanchor':'center',
    'yanchor':'top',
    'x':0.5})
    return fig

@app.callback(
    Output("gen_metrics_temp", 'figure'), 
    Output("gen_metrics_feels", 'figure'),
    Output("gen_metrics_icons", 'src'),
    [Input("states", "value")])
def general_metrics(states):
    #daily_metrics = live.copy()
    daily_metrics = live[live['state']==states]
    daily_metrics['hour'] = daily_metrics['UTC_time'].str[:2]
    daily_metrics['hour'] = daily_metrics['hour'].astype(str).astype(int)
    daily_metrics = daily_metrics.loc[daily_metrics.groupby(['city', 'state'])['hour'].idxmax()]
    daily_metrics = daily_metrics[['city', 'state','Temperature', 'feels_like','weather_description']]
    
    fig1 = go.Figure(go.Indicator(
    mode = "number",
    value = daily_metrics.Temperature.values[0],
    number = {'suffix': " °F"},
    domain = {'x': [0, 1], 'y': [0, 1]}))
    fig1.update_layout(paper_bgcolor = "lightgray")

    fig2 = go.Figure(go.Indicator(
    mode = "number",
    value = daily_metrics.feels_like.values[0],
    number = {'suffix': " °F"},
    domain = {'x': [0, 1], 'y': [0, 1]}))
    fig1.update_layout(paper_bgcolor = "lightgray")

    image = icons(daily_metrics, 'weather_description')
    return fig1, fig2, image

@app.callback(
    Output("heatmap1", "figure"), 
    Output("heatmap2", "figure"),
    Output("heatmap3", "figure"), 
    Output("heatmap4", "figure"), 
    Output("heatmap5", "figure"), 
    Output("heatmap6", "figure"),  
    Input("states", "value"))
    #Input("pollutant", "value"),)
def display_graph(states):
    df = aqi_hist.copy()
    df = df[['state','city','month', 'day', ' pm25', ' o3', ' pm10', ' no2',' so2', ' co']]
    aqi_hist_month = df.groupby(['state', 'city','month', 'day'], as_index=False).mean()
    aqi_hist_month = df.fillna(0)
    df = aqi_hist_month[aqi_hist_month['state'].eq(states)]
    
    df1 = aqi_hist_month[['month','day', ' pm25']].reset_index(drop=True)
    df1 = df1.sort_values(by=['month','day'])
    df1['Month_name'] = df1['month'].apply(lambda x: calendar.month_abbr[x])
    fig1 = go.Figure(data=go.Heatmap(
                   z=df1[' pm25'],
                   x=df1['day'],
                   y=df1['Month_name'],
                   hoverongaps = False))

    df2 = aqi_hist_month[['month','day', ' o3']].reset_index(drop=True)
    df2 = df2.sort_values(by=['month','day'])
    df2['Month_name'] = df2['month'].apply(lambda x: calendar.month_abbr[x])
    fig2 = go.Figure(data=go.Heatmap(
                   z=df2[' o3'],
                   x=df2['day'],
                   y=df2['Month_name'],
                   hoverongaps = False))

    df3 = aqi_hist_month[['month','day', ' pm10']].reset_index(drop=True)
    df3 = df3.sort_values(by=['month','day'])
    df3['Month_name'] = df3['month'].apply(lambda x: calendar.month_abbr[x])
    fig3 = go.Figure(data=go.Heatmap(
                   z=df3[' pm10'],
                   x=df3['day'],
                   y=df3['Month_name'],
                   hoverongaps = False))

    df4 = aqi_hist_month[['month','day', ' no2']].reset_index(drop=True)
    df4 = df4.sort_values(by=['month','day'])
    df4['Month_name'] = df4['month'].apply(lambda x: calendar.month_abbr[x])
    fig4 = go.Figure(data=go.Heatmap(
                   z=df4[' no2'],
                   x=df4['day'],
                   y=df4['Month_name'],
                   hoverongaps = False))

    df5 = aqi_hist_month[['month','day', ' so2']].reset_index(drop=True)
    df5 = df5.sort_values(by=['month','day'])
    df5['Month_name'] = df5['month'].apply(lambda x: calendar.month_abbr[x])
    fig5 = go.Figure(data=go.Heatmap(
                   z=df5[' so2'],
                   x=df5['day'],
                   y=df5['Month_name'],
                   hoverongaps = False))

    df6 = aqi_hist_month[['month','day', ' co']].reset_index(drop=True)
    df6 = df6.sort_values(by=['month','day'])
    df6['Month_name'] = df6['month'].apply(lambda x: calendar.month_abbr[x])
    fig6 = go.Figure(data=go.Heatmap(
                   z=df6[' co'],
                   x=df6['day'],
                   y=df6['Month_name'],
                   hoverongaps = False))

    return fig1, fig2, fig3, fig4, fig5, fig6


if __name__ == '__main__':
    app.run_server(debug=True)