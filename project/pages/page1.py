import dash
from dash import Dash, dcc, Input, html, Output, callback
from geopy.geocoders import Nominatim
import openmeteo_requests 
from retry_requests import retry
import requests_cache 
import requests
from datetime import date

today = date.today()
date_list = []
for i in range(-5,8):
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
              
            
            
        ])
        
        
        html.Div([
            dcc.RadioItems(['Fahrenheit','Celsius'],value = 'Fahrenheit',id="TempSetting")
        ]),
        
        
        html.Div([
            dcc.Checklist(['Temperature','Rain','Humidity'],['Temperature'], id = "paramSettings")#relative_humidity_2m is
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
    
    Input("TempSetting", "value")
)

def setParams(inCity,inCountry,paramSet,tempSet):  
    latlon = placeFinder.geocode({'city':inCity, 'country':inCountry})
    
    return True

#callback DateAdjustment