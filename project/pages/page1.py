import dash
from dash import Dash, dcc, Input, html, Output, callback
from geopy.geocoders import Nominatim
import openmeteo_requests 
from retry_requests import retry
import requests_cache 
import requests



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

latDefault = 0
lonDefault = 0

##add in a way for users to change these values
##have it remain unavailable until users input a city and country
##if it detects a value of 0,0 wait until available inputs
temp_set = "fahrenheit"

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude":latDefault, #function to recieve latitude from input,
    "longitude":lonDefault, #function to recieve longitude from input,
    "daily" : ["temperature_2m_max", "percipitation_sum"],
    ##add more
    "hourly":["temperature_2m","percipitation"],
    #This is where we will put in all the parameters for weather information we want to return to the user
    
    
    "current": ["temperature_2m","percipitation"],
    ##add more
    
    
    
    
    "temperature_unit": temp_set,
    #user_input (default to fahrenheit) but allow user to change to celsius.

    "past_days":7,
    
    "timezone" : "America/New_York" 
    #(Sets time zone to EST, our timezone)
}

##returned a two tiered dictionary of seperated by days? and conditions

responses = openmeteo.weather_api(url, params = params)


##response = responses[0]

layout = html.Div(
    style = {"backgroundColor":"#f1f1de"},
    children = 
    [
        html.H1("Weather Report"),
        dcc.Loading(html.Div(id = "weather-report")),
        html.Div
        ([
            
            
            html.Div
            ([
            "Input City: ",
            dcc.Input(id = "inputCity", value = '', type = 'text', autoComplete=True)
            ]),
              
            html.Div
            ([
                "Input Country: ",
                dcc.Input(id = "inputCountry", value = "", type = "text", autoComplete=True)
            ])
                
        ])
    ]
)



##we need to include callbacks somehow.
@callback(
    Input("placeholder1","placeholder2")
)
def lat_long(city,country):
    return False
