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



##setting parameters

##Variables we want to allow the user to control
##latitude and longitude via Location (input a city/country/etc)
##farenheit vs celsius



##add in a way for users to change these values
##have it remain unavailable until users input a city and country
##if it detects a value of 0,0 wait until available inputs
temp_set = "fahrenheit"

url = "https://api.open-meteo.com/v1/forecast"

##----------------------------------------------We are going to want to replace this soon with the callback function where it reads the default vvalues first and then changes them
##---------------------------------------------- Delete this later
params = {
    "latitude": 37.8, #------------------------------------------------------------------------PLACEHOLDER TO BE CHANGED------------------------------------------------
    "longitude": 22.2, #---------------------------------------------------------------------------PLACEHOLDER TO BE CHANGED-----------------------------------------------
    "daily" : ["temperature_2m_mean", "precipitation_sum"],
    ##add more
    "hourly":["temperature_2m","precipitation"],
    #This is where we will put in all the parameters for weather information we want to return to the user
    
    
    "current": ["temperature_2m","precipitation"],
    ##Poteential things we could add "is_day"
    
    
    
    
    "temperature_unit": temp_set,
    #user_input (default to fahrenheit) but allow user to change to celsius.

    "past_days":5,
    
    "timezone" : "America/New_York" 
    #(Sets time zone to EST, our timezone)
}

##returned a two tiered dictionary of seperated by days? and conditions

responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params = params)

##-----------------------------------------------------------------------------------------------------------------Above is to be deleted----------------

##response = responses[0]

layout = html.Div(
    style = {"backgroundColor":"#f1f1de"},
    children = 
    [
        html.H1("Weather Report"),
        dcc.Loading(html.Div(id = "weather-report")),
        html.Div
        ([
            
            
            html.Div(["Input City: ",
            dcc.Input(id = "inputCity", value = "Williamsburg", type = "text")]),
              
            html.Div([
                "Input Country: ",
                dcc.Input(id = "inputCountry", value = "Usa", type = "text") ])
            
            ## allow user to switch between outputting in Fahrenheit and outputting in Celsius 
        ]),
        html.Div(id="latLongOutput"),
        
        

    ]
)
html.Div([
            dcc.RadioItems(['Fahrenheit','Celsius'],value = 'Fahrenheit',id="TempSetting")
        ]) 

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





##we need to include callbacks somehow.

##callback to retrieve latitude and longitude from city and country
@callback(
    Output('latLongOutput','children'),
    Input('inputCity','value'),
    Input('inputCountry','value')
)
def get_location(city, country):
    try:
        result = placeFinder.geocode({"city":city,"country":country},timeout=5)
        lat = result.latitude
        lon = result.longitude
        return f'lat is {lat} and lon is {lon}'
    except requests.RequestException as e:
        return html.Div(f"There was an error contacting API  "{str(e)})




##Callback to retrieve new parameters
@callback(
    Input("Placeholder","Placeholder2")
)

def setParams():
    
    return()