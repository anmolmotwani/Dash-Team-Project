import dash
from dash import Dash, dcc, Input, html, Output, callback
from geopy.geocoders import Nominatim
import openmeteo_requests

dash.register_page(__name__, path = "/page1", name = "Weather Report")
## On this page we will have a layout for a user to first input the location
## Then we will retrieve that latitude and longitude from geopy and use that for the openmeteo to return weather
## we will use CSS to style a suitable layout to present basic information (Temperature, Percipitation)
## Allow users to convert from Farenheit to Celsius and vice versa




layout = html.Div(
    
    [
    ]
)

