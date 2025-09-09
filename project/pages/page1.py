import dash
from dash import html, dcc, Input, Output, callback
from geopy.geocoders import Nominatim
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd
from datetime import date

# ----- Initialize geopy and OpenMeteo -----
today = date.today()
placeFinder = Nominatim(user_agent="my_user_agent")

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Register page
dash.register_page(__name__, path="/weather", name="Weather Report")

layout = html.Div(className="weatherPage clear", children=[
    html.H1("Weather Report"),
    html.Div([
        html.Div([
            html.Label("City:"),
            dcc.Input(id="inputCity", type="text", value="Williamsburg", debounce=True)
        ]),
        html.Div([
            html.Label("Country:"),
            dcc.Input(id="inputCountry", type="text", value="USA", debounce=True)
        ])
    ], style={"display":"flex","gap":"20px","margin-bottom":"20px"}),
    
    html.Div([
        dcc.RadioItems(
            id="TempSetting",
            options=["Fahrenheit","Celsius"],
            value="Fahrenheit",
            labelStyle={'display': 'inline-block', 'margin-right':'10px'}
        ),
        dcc.Checklist(
            id="paramSettings",
            options=["Temperature","Rain","Humidity"],
            value=["Temperature"],
            labelStyle={'display': 'inline-block', 'margin-right':'10px'}
        )
    ], style={"margin-bottom":"20px"}),
    
    html.Div(id="GetWeather", className="main-card"),
    
    html.Div(dcc.Slider(0,23,1, id = "TimeSlider")),
    
    html.Div(id="forecast-cards", style={"display":"flex","overflowX":"auto","padding":"10px"})
])

# ----- Callbacks -----
@callback(
    Output("GetWeather","children"),
    Output("forecast-cards","children"),
    Input("inputCity","value"),
    Input("inputCountry","value"),
    Input("TempSetting","value"),
    Input("paramSettings","value"),
    Input("TimeSlider", "value")
)
def update_weather(city, country, tempUnit, params, time):
    try:
        # Get lat/lon
        location = placeFinder.geocode({'city':city,'country':country})
        lat, lon = location.latitude, location.longitude
        
        
        # Placeholder for API response
        current = {
            "Temperature": "75°F" if tempUnit=="Fahrenheit" else "24°C",
            "Humidity": "60%",
            "Rain": "10%"
        }
        
        apiParams = {
                    'latitude':lat,
        'longitude':lon,
        'hourly': ['temperature_2m','precipitation','relative_humidity_2m'],
        'temperature_unit':'fahrenheit',
        'past_days':3,
        }
        responses = openmeteo.weather_api(url = "https://api.open-meteo.com/v1/forecast", params = apiParams)
        response = responses[0]
        hourly = response.Hourly[0]
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
         
        hourly_data = {"date": pd.date_range(
	    start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	    end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	    freq = pd.Timedelta(seconds = hourly.Interval()),
	    inclusive = "left"
        )}
        
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["hourly_relative_humidity_2m"] = hourly_relative_humidity_2m
         
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        hourly_list = hourly_dataframe.to_numpy()
        
        # Choose background class
        bg_class = "clear"
        if "Rain" in params:
            bg_class = "rainy"
        elif "Humidity" in params:
            bg_class = "cloudy"
        
        # Current weather card
        main_card = html.Div(className=f"main-card {bg_class}", children=[
            html.H2(f"{city}, {country}"),
            html.P(f"Temperature: {hourly_list[0][1]}"),
            html.P(f"Humidity: {hourly_list[0][3]}"),
            html.P(f"Rain: {hourly_list[0][2]}")
        ])
        
        # Forecast cards placeholder
        forecast_cards = []
        for i in range(-3,4):
            forecast_cards.append(
                html.Div(className="card", children=[
                    html.P(f"Day {i}"),
                    html.P(f"Temp: {current['Temperature']}"),
                    html.P(f"Rain: {current['Rain']}")
                ])
            )
        
        return main_card, forecast_cards
    except Exception as e:
        return html.Div(f"Error fetching weather data: {str(e)}"), []

