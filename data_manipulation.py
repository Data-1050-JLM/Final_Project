
def import_data():
    
    import pandas as pd
    import numpy as np
    #from datetime import date, timedelta, datetime
    import datetime as dt

    now = dt.datetime.utcnow()
    today = now.date()

    # Bring in the live data that refresehes every hour on the 50th minute that captures the current floored hour:
    live = pd.read_csv('https://storage.googleapis.com/project-1050-data/live.csv')
    # Bring in the state abbreviations for the map graph: 
    st_codes = pd.read_csv('https://storage.googleapis.com/project-1050-data/state_codes.csv')
    live = live.join(st_codes.set_index('State'), on="state")
    live.rename(columns={"temp":"Temperature", "Alpha code":"STATE"}, inplace=True)

    # Adjust the time across 
    live['graph_date'] = live['UTC_date'] + ' '  + live['UTC_time']
    live['UTC_date'] = pd.to_datetime(live['UTC_date']).dt.date
    dtm = today - dt.timedelta(1)
    dtm = dt.datetime.strptime(str(dtm), '%Y-%m-%d').date()
    live = live[(live['UTC_date']>= dtm)]
    
    #today_dt = dt.datetime.strptime(str(now), '%Y-%m-%d').date()

    today_live = live[(live['UTC_date'] == today)]
    
    # Bring in historical AQI data:
    historic_in = pd.read_csv('https://storage.googleapis.com/project-1050-data/2021_AQI_hist.csv')
    historic = historic_in.copy()
    historic['date'] =pd.to_datetime(historic.date)
    # makoing sure that no data before current year is brought in
    historic = historic[historic['date'] >= dt.datetime(today.year, 1, 1)]
    historic = historic.sort_values(by=['date'])

    historic['month'] = pd.DatetimeIndex(historic['date']).month
    historic['day'] = pd.DatetimeIndex(historic['date']).day
    # bring in the forecast for weatherr, whihc contains about 16 days worth of data (this dat get refreshed about once week)
    weather_pred = pd.read_csv('https://storage.googleapis.com/project-1050-data/weather_pred.csv')
    weather_pred['date_time'] = pd.to_datetime(weather_pred['Date time'])
    weather_pred = weather_pred[weather_pred['date_time'] >= now]
    weather_pred = weather_pred.sort_values(by=['date_time'])


    pol_stats = today_live.copy()
    pol_stats = pol_stats[['state','aqi']]
    pol_stats['aqi'].replace('-', '0', inplace=True)
    pol_stats['aqi'] = pol_stats['aqi'].astype(float)
    
    usa_stats = today_live.copy()
    usa_stats['hour'] = pd.DatetimeIndex(usa_stats['UTC_time']).hour
    usa_stats = usa_stats[['UTC_time', 'state', 'city', 'aqi', 'hour']]
    usa_stats = usa_stats.loc[usa_stats.groupby(['city', 'state'])['hour'].idxmax()]
    usa_stats = usa_stats.dropna(axis = 0)
    usa_stats = usa_stats[['hour', 'aqi']]
    usa_stats['aqi'] = usa_stats['aqi'].astype(float)
    usa_stats = usa_stats.groupby(['hour'], as_index = False)['aqi'].mean().round(2)

    states = {'Alaska':['AK','O',733391],'Alabama':['AL', 'S',5024279],'Arkansas':['AR','S',3011524], 'Arizona':['AZ','W',7151502],'California':['CA','W',39538223], 'Colorado':['CO','W',5773714], 'Connecticut':['CT','N',3605944],'Delaware':['DE','N',989948],'Florida':['FL','S',21538187],'Georgia':['GA','S',10711908],'Hawaii':['HI','O',1455271],'Iowa':['IA','M',3190369],'Idaho':['ID','W',1839106],'Illinois':['IL','M',12812508],'Indiana':['IN','M',6785528],'Kansas':['KS', 'M',2937880],'Kentucky':['KY', 'S',4505836], 'Louisiana':['LA','S',4657757],'Massachusetts':['MA','N',7029917],'Maryland':['MD','N',6177224],'Maine':['ME','N',1362359],'Michigan':['MI','W',10077331],'Minnesota':['MN','M',5706494], 'Montana':['MO','M',6154913], 'Mississippi':['MS','S',2961279],'Montana':['MT','W',1084225],'North Carolina':['NC','S',10439388], 'North Dakota':['ND','M',779094],'Nebraska':['NE','W',1961504],'New Hampshire':['NH','N',1377529],'New Jersey':['NJ','N',9288994], 'New Mexico':['NM','W',2117522], 'Nevada':['NV','W',3104614],'New York':['NY','N',20201249],'Ohio':['OH','M',11799448],'Oklahoma':['OK','S',3959353], 'Oregon':['OR','W',4237256], 'Pennsylvania':['PA', 'N',13002700],'Rhode Island':['RI','N',1097379],'South Carolina':['SC','S',5118425], 'South Dakota':['SD','M',886667],'Tennessee':['TN','S',6910840], 'Texas':['TX','S',29145505], 'Utah':['UT','W',3271616], 'Virginia':['VA','S',8631393], 'Vermont':['VT','N',643077], 'Washington':['WA','W',7705281],'Wisconsin':['WI','M',5893718],'West Virginia':['WV','S',1793716], 'Wyoming':['WY','W',576851]}
    state_abrev = {}
    state_region = {}
    state_pop = {}
    for k, v in states.items():
        state_abrev[k] = v[0]
        state_region[k] = v[1]
        state_pop[k] = v[2]
    region_df = historic_in.copy()
    region_df['region'] = region_df['state'].map(state_region)
    region_df['abrev'] = region_df['state'].map(state_abrev)
    region_df['pop'] = region_df['state'].map(state_pop)
    region_df["region"].replace({"O": "Other", "W": "West", "N": "North", "S":"South", "M":"Midwest"}, inplace=True)
    region_df = region_df[['state', 'city','date','region','pop',' pm25', ' o3', ' pm10', ' no2',' so2', ' co']]
    region_df = region_df.fillna(0)

    return live , today_live, historic , weather_pred, pol_stats, region_df, usa_stats
