

def icons(df, weather_col):
     from PIL import Image
     import pandas as pd
     import pandas as pd
     import numpy as np
    
     if df[weather_col].iloc[0] == "clear sky":
          img ='./assets/images/{icon}'.format(icon='sunny.jpg')
     elif df[weather_col].iloc[0] == "few clouds":
          img ='./assets/images/{icon}'.format(icon='overcast.png')
     elif "clouds" in df[weather_col].iloc[0]:
          img ='./assets/images/{icon}'.format(icon='cloudy.png')
     elif df[weather_col].iloc[0] == "snow":
          img ='./assets/images/{icon}'.format(icon='snow.png')
     elif df[weather_col].iloc[0] == "drizzle":
          img ='./assets/images/{icon}'.format(icon='drizzle.png')
     elif "rain" in df[weather_col].iloc[0]:
          img ='./assets/images/{icon}'.format(icon='raining2.png')
     elif df[weather_col].iloc[0] == "thunderstorm":
          img ='./assets/images/{icon}'.format(icon='thunderstorm.png')
     elif df[weather_col].iloc[0] == "mist":
          img ='./assets/images/{icon}'.format(icon='mist.png')
     else:
          img ='./assets/images/{icon}'.format(icon='question.png')
     
     return img
