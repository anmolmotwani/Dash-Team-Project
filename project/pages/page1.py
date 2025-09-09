import dash
from dash import html, dcc, Input, Output, callback
from geopy.geocoders import Nominatim
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd

# ----- Initialize geopy and OpenMeteo -----
placeFinder = Nominatim(user_agent="my_user_agent")

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Register page
dash.register_page(__name__, path="/weather", name="Weather Report")

# --- Animated icon snippets ---
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
    ], style={"display": "flex", "gap": "20px", "margin-bottom": "20px"}),

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

    # Icon goes here
    html.Div(id="weather-icon", style={"margin": "6px 0 12px"}),

    html.Div(id="GetWeather", className="main-card"),

    html.Div(id="forecast-cards", style={"display": "flex", "overflowX": "auto", "padding": "10px"})
])

# ----- Callbacks -----
@callback(
    Output("GetWeather", "children"),
    Output("forecast-cards", "children"),
    Output("weather-icon", "children"),
    Input("inputCity", "value"),
    Input("inputCountry", "value"),
    Input("TempSetting", "value"),
    Input("paramSettings", "value"),
)
def update_weather(city, country, tempUnit, params):
    try:
        # Geocode (city + country); for states like "Arizona", prefer a city (e.g., Phoenix) for better comparability
        location = placeFinder.geocode({"city": city, "country": country}, timeout=10)
        if not location:
            raise ValueError("Location not found.")
        lat, lon = location.latitude, location.longitude

        # Units per TempSetting
        temp_unit = "fahrenheit" if tempUnit.lower().startswith("f") else "celsius"
        unit_symbol = "°F" if temp_unit == "fahrenheit" else "°C"

        # Call Open-Meteo hourly endpoint
        apiParams = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "hourly": ["temperature_2m", "precipitation", "relative_humidity_2m"],
            "temperature_unit": temp_unit,
            "past_days": 1,   # we only need recent history to find 'now'
            "forecast_days": 1,
        }
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=apiParams)
        response = responses[0]
        hourly = response.Hourly()  # method call

        # Arrays
        temp_arr   = hourly.Variables(0).ValuesAsNumpy()
        precip_arr = hourly.Variables(1).ValuesAsNumpy()
        humid_arr  = hourly.Variables(2).ValuesAsNumpy()

        # Local time index (tz-aware)
        t_start = pd.to_datetime(hourly.Time(),    unit="s", utc=True)
        t_end   = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True)
        step    = pd.Timedelta(seconds=hourly.Interval())
        dt_index = pd.date_range(start=t_start, end=t_end, freq=step, inclusive="left")  # tz-aware (UTC)

        # Open-Meteo uses the requested timezone for values, but timestamps are given with tz info.
        # Convert to that tz for "now" comparison.
        # Determine the tz from the index (e.g., America/Phoenix)
        local_tz = dt_index.tz
        now_local = pd.Timestamp.now(tz=local_tz)

        df = pd.DataFrame({
            "time": dt_index,                # tz-aware
            "temperature": temp_arr,
            "precip": precip_arr,
            "humidity": humid_arr
        })

        # Select the hour CLOSEST to local 'now' (fixes the early-morning/next-day bug)
        i_closest = (df["time"] - now_local).abs().idxmin()
        row = df.loc[i_closest]
        display_time = row["time"].tz_convert(None).strftime("%Y-%m-%d %H:%M")

        # Format values
        temp_txt = f"{row['temperature']:.1f}{unit_symbol}"
        hum_txt  = f"{row['humidity']:.0f}%"
        rain_txt = f"{row['precip']:.2f} mm"

        # Decide background + icon from real values
        if row["precip"] > 0.2:
            bg_class, icon = "rainy", rain_icon()
        elif row["humidity"] >= 70:
            bg_class, icon = "cloudy", cloud_icon()
        else:
            bg_class, icon = "clear", sun_icon()

        # Current weather card
        pieces = [
            html.H2(f"{city.title()}, {country.upper()}"),
            html.P(f"Time: {display_time}")
        ]
        if "Temperature" in params: pieces.append(html.P(f"Temperature: {temp_txt}"))
        if "Humidity"   in params: pieces.append(html.P(f"Humidity: {hum_txt}"))
        if "Rain"       in params: pieces.append(html.P(f"Rain: {rain_txt}"))

        main_card = html.Div(className=f"main-card {bg_class}", children=pieces)

        # Forecast cards (still simple placeholders using current reading)
        forecast_cards = []
        for i in range(-3, 4):
            forecast_cards.append(
                html.Div(className="card", children=[
                    html.P(f"Day {i}"),
                    html.P(f"Temp: {temp_txt}"),
                    html.P(f"Rain: {rain_txt}")
                ])
            )

        return main_card, forecast_cards, icon

    except Exception as e:
        return html.Div(f"Error fetching weather data: {str(e)}", className="main-card"), [], html.Div()
