import dash
from dash import html, dcc, Input, Output, callback
from geopy.geocoders import Nominatim
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd
import plotly.express as px

# Setup geolocation and API client
placeFinder = Nominatim(user_agent="weather_app")
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

dash.register_page(__name__, path="/weather", name="Weather Report")

# --- Animated icon functions ---
def sun_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="icon sun", children=[
            html.Div(className="sun-core"),
            html.Div(className="sun-rays")
        ])
    ])

def cloud_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="icon cloud", children=[
            html.Div(className="cloud-bubble b1"),
            html.Div(className="cloud-bubble b2"),
            html.Div(className="cloud-bubble b3"),
        ])
    ])

def rain_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="icon rain", children=[
            html.Div(className="cloud-bubble b1"),
            html.Div(className="cloud-bubble b2"),
            html.Div(className="cloud-bubble b3"),
            html.Span(className="drop d1"),
            html.Span(className="drop d2"),
            html.Span(className="drop d3"),
        ])
    ])

# --- Layout ---
layout = html.Div(className="weatherPage clear", children=[
    html.H1("Weather Report"),
    html.Div([
        dcc.Input(id="inputCity", type="text", value="Williamsburg", debounce=True, placeholder="City"),
        dcc.Input(id="inputCountry", type="text", value="USA", debounce=True, placeholder="Country")
    ], style={"display": "flex", "gap": "10px", "margin-bottom": "20px"}),

    html.Div([
        dcc.RadioItems(
            id="TempSetting",
            options=["Fahrenheit", "Celsius"],
            value="Fahrenheit",
            labelStyle={"display": "inline-block", "margin-right": "10px"}
        ),
        dcc.Checklist(
            id="paramSettings",
            options=["Temperature", "Rain", "Humidity"],
            value=["Temperature"],
            labelStyle={"display": "inline-block", "margin-right": "10px"}
        )
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Checklist(
            id="toggleChart",
            options=[{"label": "Show Hourly Chart", "value": "show"}],
            value=["show"]
        ),
        dcc.Dropdown(
            id="extraMetric",
            options=[
                {"label": "Feels Like Temp", "value": "feels_like"},
                {"label": "Wind Speed", "value": "wind"}
            ],
            placeholder="Select extra metric",
            style={"width": "300px", "margin-top": "10px"}
        )
    ], style={"margin-bottom": "20px"}),

    html.Div(id="weather-icon", style={"margin": "6px 0 12px"}),
    html.Div(id="GetWeather", className="main-card"),
    html.Div(id="forecast-cards", style={"display": "flex", "overflowX": "auto", "padding": "10px"}),

    html.Div(id="extraMetricDisplay", style={"margin": "20px 0"}),

    html.Div(id="chart-container", children=[
        html.H3("Hourly Temperature Trend"),
        dcc.Graph(id="temp-chart")
    ])
])

# --- Callback 1: Current Weather ---
@callback(
    Output("GetWeather", "children"),
    Output("weather-icon", "children"),
    Input("inputCity", "value"),
    Input("inputCountry", "value"),
    Input("TempSetting", "value"),
    Input("paramSettings", "value")
)
def update_weather_card(city, country, unit, params):
    try:
        location = placeFinder.geocode(f"{city}, {country}", timeout=10)
        if not location:
            raise ValueError("Location not found.")
        lat, lon = location.latitude, location.longitude

        temp_unit = "fahrenheit" if unit.lower().startswith("f") else "celsius"
        symbol = "°F" if temp_unit == "fahrenheit" else "°C"

        params_api = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "temperature_unit": temp_unit,
            "hourly": ["temperature_2m", "precipitation", "relative_humidity_2m"]
        }
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params_api)[0]
        hourly = response.Hourly()

        df = pd.DataFrame({
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                periods=len(hourly.Variables(0).ValuesAsNumpy()),
                freq=pd.Timedelta(seconds=hourly.Interval())
            ),
            "temperature": hourly.Variables(0).ValuesAsNumpy(),
            "precip": hourly.Variables(1).ValuesAsNumpy(),
            "humidity": hourly.Variables(2).ValuesAsNumpy()
        })

        now = pd.Timestamp.now(tz=df["time"].dt.tz)
        current = df.iloc[(df["time"] - now).abs().idxmin()]

        icon = sun_icon()
        if current["precip"] > 0.2:
            icon = rain_icon()
        elif current["humidity"] > 70:
            icon = cloud_icon()

        card = html.Div(className="main-card clear", children=[
            html.H2(f"{city.title()}, {country.upper()}"),
            html.P(f"Time: {current['time'].tz_convert(None).strftime('%Y-%m-%d %H:%M')}"),
            html.P(f"Temperature: {current['temperature']:.1f}{symbol}") if "Temperature" in params else None,
            html.P(f"Humidity: {current['humidity']:.0f}%") if "Humidity" in params else None,
            html.P(f"Rain: {current['precip']:.2f} mm") if "Rain" in params else None
        ])

        return card, icon

    except Exception as e:
        return html.Div(f"Error: {str(e)}"), html.Div()

# --- Callback 2: Forecast Cards ---
@callback(
    Output("forecast-cards", "children"),
    Input("inputCity", "value"),
    Input("inputCountry", "value"),
    Input("TempSetting", "value")
)
def update_forecast_cards(city, country, unit):
    try:
        location = placeFinder.geocode(f"{city}, {country}", timeout=10)
        if not location:
            raise ValueError("Location not found.")
        lat, lon = location.latitude, location.longitude

        temp_unit = "fahrenheit" if unit.lower().startswith("f") else "celsius"
        symbol = "°F" if temp_unit == "fahrenheit" else "°C"

        params_api = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "temperature_unit": temp_unit,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "forecast_days": 5
        }
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params_api)[0]
        daily = response.Daily()

        df = pd.DataFrame({
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                periods=len(daily.Variables(0).ValuesAsNumpy()),
                freq="D"
            ),
            "tmax": daily.Variables(0).ValuesAsNumpy(),
            "tmin": daily.Variables(1).ValuesAsNumpy(),
            "rain": daily.Variables(2).ValuesAsNumpy()
        })

        cards = []
        for i, row in df.iterrows():
            cards.append(html.Div(className="card", children=[
                html.P(f"Day {i+1}"),
                html.P(f"Temp: {(row['tmax'] + row['tmin'])/2:.1f}{symbol}"),
                html.P(f"Rain: {row['rain']:.2f} mm")
            ]))

        return cards

    except Exception as e:
        return [html.Div(f"Error: {str(e)}")]

# --- Callback 3: Temperature Chart ---
@callback(
    Output("temp-chart", "figure"),
    Input("inputCity", "value"),
    Input("inputCountry", "value"),
    Input("TempSetting", "value")
)
def update_temp_chart(city, country, unit):
    try:
        location = placeFinder.geocode(f"{city}, {country}", timeout=10)
        if not location:
            raise ValueError("Location not found.")
        lat, lon = location.latitude, location.longitude

        temp_unit = "fahrenheit" if unit.lower().startswith("f") else "celsius"
        symbol = "°F" if temp_unit == "fahrenheit" else "°C"

        params_api = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "temperature_unit": temp_unit,
            "hourly": ["temperature_2m"],
            "past_days": 3,
            "forecast_days": 4
        }
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params_api)[0]
        hourly = response.Hourly()

        df = pd.DataFrame({
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                periods=len(hourly.Variables(0).ValuesAsNumpy()),
                freq=pd.Timedelta(seconds=hourly.Interval())
            ),
            "temperature": hourly.Variables(0).ValuesAsNumpy()
        })

        fig = px.line(df, x="time", y="temperature", title=f"Hourly Temperature ({symbol})")
        fig.update_layout(margin={"t":40, "b":20}, height=300)

        return fig

    except Exception as e:
        return px.line(title=f"Error: {str(e)}")
@callback(
    Output("chart-container", "style"),
    Input("toggleChart", "value")
)
def toggle_chart_display(value):
    if "show" in value:
        return {"display": "block"}
    return {"display": "none"}
@callback(
    Output("extraMetricDisplay", "children"),
    Input("extraMetric", "value"),
    Input("inputCity", "value"),
    Input("inputCountry", "value")
)
def update_extra_metric(metric, city, country):
    try:
        location = placeFinder.geocode(f"{city}, {country}", timeout=10)
        if not location:
            raise ValueError("Location not found.")
        lat, lon = location.latitude, location.longitude

        params_api = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "hourly": ["apparent_temperature", "windspeed_10m"],
            "forecast_days": 1
        }
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params_api)[0]
        hourly = response.Hourly()

        if metric == "feels_like":
            value = hourly.Variables(0).ValuesAsNumpy()[0]
            return html.P(f"Feels Like Temperature: {value:.1f}°")
        elif metric == "wind":
            value = hourly.Variables(1).ValuesAsNumpy()[0]
            return html.P(f"Wind Speed: {value:.1f} m/s")
        else:
            return html.P("Select a metric to display.")

    except Exception as e:
        return html.P(f"Error loading metric: {str(e)}")
    