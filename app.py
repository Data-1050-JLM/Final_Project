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

live, today_live, aqi_hist, weather_pred, pol_stats, region_df = import_data()


def weather_description():
    """
    Returns weather dashboard description in markdown. Default is Providence, Rhode Island
    """
    return html.Div(children=[dcc.Markdown('''
        ## State Level Analysis Across the United States
        
        #### Knowing the weather and air quality is becoming increasingly important with all the current events, such as global warming, wildfires, and COVID. According to the World Health Organization (WHO), air pollution is responsible for 7 million deaths per year. We want to provide a one-stop dashboard for not only the current and forecast, but also historic air quality data that users can interact with. This dashboard contains live weather information and air quality index (AQI) on the hour, weather predictions, and historic AQI across 50 state capitals in the USA.
        
        #### Temperature is measured in Fahrenheit and time is reported in Universal Time (UTC). The major pollutants are ozone (O3), particulate matter 2.5 and 10 (PM 2.5 and PM 10), Sulphur Dioxide (SO2), Carbon Monoxide (CO), and Nitrogen Dioxide (NO2).
        
        #### Feel free to interact with the dashboard! Zoom into the map, hover over data points, slide the date bar to compare AQI's of neighboring states, or see the differences between pollutants over the past year.
        
        ### Please select a state
        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

def air_quality_historic_description():
    """
    Returns aqi historic description in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        ## Air Pollutants Over The Past Year
        
        ##### Note: the graphs below may take up to 30 seconds to load!
        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

def heatmap(): 
    """
    Returns heatmap description in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        ##### Heatmap Displaying Data of Selected Air Pollutant
        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

def data_source(): 
    """
    Returns data source description in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        ##### GitHub: 
        ##### https://github.com/Data-1050-JLM/Final_Project
        ##### Data Source:
        ##### Live Weather [OpenWeather](http://openweathermap.org/) **updates every hour**
        ##### Live Air Quality Index [The World Air Quality Project](http://aqicn.org/) **updates every hour**
        ##### Historic Air Quality Index [The World Air Quality Project](http://aqicn.org/) **updates every week**
        ##### Weather Forecast [Visual Corssing](https://www.visualcrossing.com) **updates every week**
        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
        html.P("Weather and Air Quality Tracker"),
        weather_description(),
        dcc.Dropdown(
        id='states', 
        options=[{'value': x, 'label': x} 
                 for x in live['state']],
        value="Rhode Island"),

        
        dcc.Graph(id='gen_metrics_temp', style={'height':'30%','width': '20%','display': 'inline-block'}),
        dcc.Graph(id='gen_metrics_feels', style={'height':'30%','width': '20%','display': 'inline-block'} ),
        dash.html.Img(id='gen_metrics_icons', style={'height':'30%','width': '20%','display': 'inline-block',  
        'padding-top': '50px','padding-bottom': '50px' } ),
        dcc.Graph(id='gen_metrics_stateAQI', style={'height':'30%','width': '20%','display': 'inline-block'} ),
        dcc.Graph(id='gen_metrics_usAQI', style={'height':'30%','width': '20%','display': 'inline-block'} ),
        #dcc.Graph(id="bar", style={'height':'30%','width': '30%','display': 'inline-block'} ),

        dcc.Graph(id="USA_MAP",style={'width': '50%','display': 'inline-block'}),
        dcc.Graph(id="bar_line", style={'width': '50%','display': 'inline-block'}),
        dcc.Graph(id="Weahter_forecast", style={'width': '100%'}),
    
        air_quality_historic_description(),
        dcc.Graph(id='slideshow', style={'display': 'inline-block', "width":"100%"}),
        heatmap(),
        dcc.Tabs([
        dcc.Tab(label='pm2.5', children=[
            dcc.Graph(id='heatmap1', style={'display': 'inline'})
        ],style={'display': 'inline-block'}),
        dcc.Tab(label='o3', children=[
            dcc.Graph(id='heatmap2', style={'display': 'inline'})
        ],style={'display': 'inline-block'}),
        dcc.Tab(label='pm10', children=[
            dcc.Graph(id='heatmap3', style={'display': 'inline'})
        ],style={'display': 'inline-block'}),
         dcc.Tab(label='no2', children=[
            dcc.Graph(id='heatmap4', style={'display': 'inline'})
        ],style={'display': 'inline-block'}),
         dcc.Tab(label='so2', children=[
            dcc.Graph(id='heatmap5', style={'display': 'inline'})
        ],style={'display': 'inline-block'}),
         dcc.Tab(label='co', children=[
            dcc.Graph(id='heatmap6', style={'display': 'inline'})
        ],style={'display': 'inline-block'})], style={'display': 'inline-block'}),
        data_source()
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
         'yanchor': 'top'
        },
                 plot_bgcolor='rgb(255,255,255)',
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
        template= "simple_white"
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
    Output("gen_metrics_stateAQI", 'figure'),
    Output("gen_metrics_usAQI", 'figure'),
    Output("gen_metrics_icons", 'src'),
    [Input("states", "value")])
def general_metrics(states):
    daily_metrics = today_live[today_live['state']==states]
    daily_metrics['hour'] = daily_metrics['UTC_time'].str[:2]
    daily_metrics['hour'] = daily_metrics['hour'].astype(str).astype(int)
    daily_metrics = daily_metrics.loc[daily_metrics.groupby(['state','UTC_date'])['hour'].idxmax()]
    daily_metrics = daily_metrics[['state','Temperature', 'feels_like','weather_description']]
    
    fig1 = go.Figure(go.Indicator(
    mode = "number",
    value = daily_metrics.Temperature.values[0],
    number = {'suffix': " °F", 'font': {"size":65 }},
        title = {"text": "Current Temperature<br><span style='font-size:0.8em;color:gray'>{state}</span>".format(state=states)},
    domain = {'x': [0, 1], 'y': [0, 1]}))
 
    fig2 = go.Figure(go.Indicator(
    mode = "number",
    value = daily_metrics.feels_like.values[0],
    number = {'suffix': " °F", 'font': {"size":65 }},
        title = {"text": "Feels like<br><span style='font-size:0.8em;color:gray'>{state}</span>".format(state=states)},
    domain = {'x': [0, 1], 'y': [0, 1]}))

    cur_state = pol_stats[pol_stats['state'].eq(states)]
    cur_state = cur_state.melt(id_vars=["state"], 
        var_name="Pollution", 
        value_name="Value")


    fig3 = go.Figure(go.Indicator(
    mode = "number",
    value = cur_state.Value.values[0],
        number = {'font': {"size":65 }},
        title = {"text": "Current State AQI<br><span style='font-size:0.8em;color:gray'>{state}</span>".format(state=states)},
    domain = {'x': [0, 1], 'y': [0, 1]}))

    fig4 = go.Figure(go.Indicator(
    mode = "number",
    value = pol_stats.aqi.mean(),
        number = {'font': {"size":65 }},
        title = {"text": "Average State AQI<br><span style='font-size:0.8em;color:gray'>Overall</span>"},
    domain = {'x': [0, 1], 'y': [0, 1]}))

    image = icons(daily_metrics, 'weather_description')
    return fig1, fig2, fig3, fig4, image

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
    
    df1 = df[['month','day', ' pm25']].reset_index(drop=True)
    df1 = df1.sort_values(by=['month','day'])
    df1['Month_name'] = df1['month'].apply(lambda x: calendar.month_abbr[x])
    fig1 = go.Figure(data=go.Heatmap(
                   z=df1[' pm25'],
                   x=df1['day'],
                   y=df1['Month_name'],
                   hoverongaps = False))

    df2 = df[['month','day', ' o3']].reset_index(drop=True)
    df2 = df2.sort_values(by=['month','day'])
    df2['Month_name'] = df2['month'].apply(lambda x: calendar.month_abbr[x])
    fig2 = go.Figure(data=go.Heatmap(
                   z=df2[' o3'],
                   x=df2['day'],
                   y=df2['Month_name'],
                   hoverongaps = False))

    df3 = df[['month','day', ' pm10']].reset_index(drop=True)
    df3 = df3.sort_values(by=['month','day'])
    df3['Month_name'] = df3['month'].apply(lambda x: calendar.month_abbr[x])
    fig3 = go.Figure(data=go.Heatmap(
                   z=df3[' pm10'],
                   x=df3['day'],
                   y=df3['Month_name'],
                   hoverongaps = False))

    df4 = df[['month','day', ' no2']].reset_index(drop=True)
    df4 = df4.sort_values(by=['month','day'])
    df4['Month_name'] = df4['month'].apply(lambda x: calendar.month_abbr[x])
    fig4 = go.Figure(data=go.Heatmap(
                   z=df4[' no2'],
                   x=df4['day'],
                   y=df4['Month_name'],
                   hoverongaps = False))

    df5 = df[['month','day', ' so2']].reset_index(drop=True)
    df5 = df5.sort_values(by=['month','day'])
    df5['Month_name'] = df5['month'].apply(lambda x: calendar.month_abbr[x])
    fig5 = go.Figure(data=go.Heatmap(
                   z=df5[' so2'],
                   x=df5['day'],
                   y=df5['Month_name'],
                   hoverongaps = False))

    df6 = df[['month','day', ' co']].reset_index(drop=True)
    df6 = df6.sort_values(by=['month','day'])
    df6['Month_name'] = df6['month'].apply(lambda x: calendar.month_abbr[x])
    fig6 = go.Figure(data=go.Heatmap(
                   z=df6[' co'],
                   x=df6['day'],
                   y=df6['Month_name'],
                   hoverongaps = False))

    return fig1, fig2, fig3, fig4, fig5, fig6

@app.callback(
    Output("slideshow", "figure"), 
    [Input("states", "value")])
def display_graph(states):
    df_get_region = region_df[region_df['state'].eq(states)]
    region = df_get_region['region'].iloc[0]
    regional_df = region_df[region_df['region'].eq(region)]
    regional_df['month'] = pd.DatetimeIndex(regional_df['date']).month
    regional_df['day'] = pd.DatetimeIndex(regional_df['date']).day

    fig = px.scatter(regional_df, x="day",  
            y=" pm25", 
            animation_frame="date", animation_group="state",
           size="pop", color="state", hover_name="state", facet_col="region", text="state",
           title="Comparing AQI of {state}\'s Neighboring States".format(state=states), 
            size_max=45, range_x=[1,31],range_y=[0,90],
            template= "simple_white")

    fig.update_layout(
        autosize=False,
        xaxis = dict(
        range=[1,31], # update
        tickmode = 'array',
        tickvals = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
    ),)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
