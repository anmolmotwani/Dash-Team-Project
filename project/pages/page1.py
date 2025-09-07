import dash
from dash import Dash, dcc, Input, html, Output, callback
from geopy.geocoders import Nominatim
import openmeteo_requests 
from retry_requests import retry
import requests_cache


dash.register_page(__name__, path = "/page1", name = "Weather Report")
## On this page we will have a layout for a user to first input the location
## Then we will retrieve that latitude and longitude from geopy and use that for the openmeteo to return weather
## we will use CSS to style a suitable layout to present basic information (Temperature, Percipitation)
## Allow users to convert from Farenheit to Celsius and vice versa


##taken directly from the open-meteo API. Do we keep this here???
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

##setting parameters

##Variables we want to allow the user to control
##latitude and longitude via Location (input a city/country/etc)
##farenheit vs celsius

url = "https://api.open-meteo.com/v1/forecast"
params = {
    #"latitude": function to recieve latitude from input
    #"longitude": function to recieve longitude from input
    #"daily" : ["temperature_2m_max", "percipitation_sum",...]
    #"hourly":["temperature_2m","rain",...] This is where we will put in all the parameters for weather information
    #we want to return to the user
    #"current": ["temperature_2m","rain",...]
    
    
    #"temperature_unit": user_input (default to fahrenheit) but allow user to change to celsius.

    #"past_days":7
    
    #"timezone" : "America/New_York" (Sets time zone to EST, our timezone)
}

##returned a two tiered dictionary of seperated by days? and conditions

responses = openmeteo.weather_api(url, params = params)


##response = responses[0]

layout = html.Div(
    
    [
    
    ]
)

