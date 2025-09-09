import dash
from dash import Dash, dcc, Input, html, Output, callback
from geopy.geocoders import Nominatim
import openmeteo_requests 
import pandas as pd
from retry_requests import retry
import requests_cache 
import requests
from datetime import date

today = date.today()
date_list = []
for i in range(-7,8):
    x = today.day + i
    y = today.replace(day = x)
    date_list.append(y)



placeFinder = Nominatim(user_agent="my_user_agent")

dash.register_page(__name__, path = "/page1", name = "Weather Report")
## On this page we will have a layout for a user to first input the location
## Then we will retrieve that latitude and longitude from geopy and use that for the openmeteo to return weather
## we will use CSS to style a suitable layout to present basic information (Temperature, Percipitation)
## Allow users to convert from Farenheit to Celsius and vice versa


##I think what this does is instantiate the openmeteo so instead of doing requests.get we use this...i think
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)




temp_set = "fahrenheit"

url = "https://api.open-meteo.com/v1/forecast"




layout = html.Div(
    [
        html.H1("Weather Report"),
        dcc.Loading(html.Div(id = "weather-report")),
        html.Div
        ([
            
            
            html.Div(["Input City: ",
            dcc.Input(id = "inputCity", value = "Williamsburg", type = "text",debounce=2)]),
            
            html.Div(["Input Country: ",
                      dcc.Input(id = "inputCountry", value = "USA", type="text",debounce=2)])
              
            
            
        ]),
        
        
        html.Div([
            dcc.RadioItems(['Fahrenheit','Celsius'],value = 'Fahrenheit',id="TempSetting")
        ]),
        
        
        html.Div([
            dcc.Checklist(['Temperature','Rain','Humidity'],['Temperature'], id = "paramSettings")#relative_humidity_2m is
        ]),
        
        html.Div([
            dcc.Slider(0,23,1, value = 0, id = "timeslider")
        ]),
            html.Div([
            dcc.Slider(0,14,1, value = 0, id = "dayslider")
        ]),
        
       html.Div(id="GetWeather")
        


    ]
)




##How ddo we get the website to display the informationn in an appropriate manner?
## We need html and we should have a list.
## have it be centered top it says the temperature and city
##example


##       86F
##   Williamsburg
## Percipitation: 10%


##Slider with date ranges from 7 days past and 7 days future
##slider default to today and have it say today in the center
## dcc.Slider(0,14, marks ={i'{date_list[i]}' for i in range(14), value = 7})

##Checkboxes for data
##dcc.Checklist(['Percipitation', 'Humidity', 'Wind Speed'], 'Percipitation')
##This would allow people to turn on or off certain pieces of data shown. Percipitaiton would be on by default

##Radio for Celsius/Farenheit
##dcc.RadioItems(['Celsius','Farenheit'], 'Farenheit')

##----------------------------------------------------------------------------------------Change to one callback-------------------

##callback to retrieve latitude and longitude from city and country
# @callback(
#     Output('latlonOutput','children'),
#     Input("inputAddress",'value')
          
# )
# def get_location(address):
#     try:
#         result = placeFinder.geocode(address, exactly_one=True)
#         latlonlist = []
#         latlonlist.append(result.latitude)
#         latlonlist.append(result.longitude)
#         if result != None:
#             return (latlonlist)
#         else:
#             return ("Error, location you entered was not available.")
#     except requests.RequestException as e:
#         return html.Div(f"There was an error contacting API  {str(e)}")
##Callback to retrieve new parameters
@callback(
    Output('GetWeather', 'children'),
    
    Input('inputCity','value'),
    
    Input('inputCountry','value'),
    
    Input('paramSettings', 'value'),
    
    Input("TempSetting", "value"),
    
    Input("timeslider","value"),
    
    Input("dayslider", "value")
)

def setParams(inCity,inCountry,paramSet,tempSet, timeGet, dayGet):  
    paramTemp = False
    paramRain = False
    paramHumid = False
    temp_set = "fahrenheit"
    try:
        latlon = placeFinder.geocode({'city':inCity, 'country':inCountry},timeout=2)
    except:
        print("Error")
    
    if tempSet == "Celsius":
        temp_set = "celsius"
    
    params = {
        'latitude':latlon.latitude,
        'longitude':latlon.longitude,
        'hourly': ['temperature_2m','precipitation','relative_humidity_2m'],
        'temperature_unit':temp_set,
        "past_days":7,
    }
    responses = openmeteo.weather_api(url = "https://api.open-meteo.com/v1/forecast", params = params)
    response = responses[0]
    hourly = response.Hourly()
    
    
    if ('Temperature' and 'Rain' and 'Humidity') not in paramSet:
        print("Error, please include a parameter")
    
    if 'Temperature' in paramSet:
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        paramTemp = True
    if 'Rain' in paramSet:
        hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
        paramRain = True
    if 'Humidity' in paramSet:
        hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
        paramHumid = True
    
    ##taken directly from open meteo documentation for testing
    
    hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
    )}
    
    
    if paramTemp:
        hourly_data["temperature_2m"] = hourly_temperature_2m
    if paramRain:
        hourly_data["precipitation"] = hourly_precipitation
    if paramHumid:
        hourly_data["hourly_relative_humidity_2m"] = hourly_relative_humidity_2m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_list = hourly_dataframe.to_numpy()
    print("\nHourly data\n", hourly_dataframe)
    
    timeRef = 0
    
    for a in range(int(dayGet)):
        timeRef+=24
    for b in range(int(timeGet)):
        timeRef+=1
            
    
    x = f"The Date is 09/{2+dayGet}/2025 at {timeGet}:00 Hours \n"
    if paramTemp:
        x += f"\n Temperature {hourly_list[timeRef][1]:.2f}"
        if paramRain:
            x+= f"\n\n Precipitation Level: {hourly_list[timeRef][2]}"
            if paramHumid:
                x+= f"\n Humidity {hourly_list[timeRef][3]}"
        elif paramHumid:
            x+= f"\n Humidity {hourly_list[timeRef][2]}"
    elif paramRain:
        x+= f"\n Precipitation level: {hourly_list[timeRef][1]}"
        if paramHumid:
            x+= f"\n Humidity {hourly_list[timeRef][2]}"
    elif paramHumid:
        x+= f"\n Humidity {hourly_list[timeRef][1]}"
        
                
    return x
    ###Column 0 [x][0] represents date and time 
    ##starts at 0:00 Today -7 days, ends at 23:00 today +7 days
    ##Column 1 [x][0] represents the temperature with 6 decimal points
    
#callback DateAdjustment
