<<<<<<< Updated upstream
import dash
from dash import html, dcc, Input, Output, callback
from geopy.geocoders import Nominatim
import requests_cache
from retry_requests import retry
import openmeteo_requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----- Initialize geopy and OpenMeteo -----
placeFinder = Nominatim(user_agent="my_user_agent")
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Register page
dash.register_page(__name__, path="/weather", name="Weather Report")

# --- Animated icon snippets (namespaced classes) ---
def sun_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="wx-icon sun", children=[
            html.Div(className="sun-core"),
            html.Div(className="sun-rays")
        ])
    ])

def cloud_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="wx-icon cloud", children=[
            html.Div(className="cloud-bubble b1"),
            html.Div(className="cloud-bubble b2"),
            html.Div(className="cloud-bubble b3"),
        ])
    ])

def rain_icon():
    return html.Div(className="weather-icon-wrap", children=[
        html.Div(className="wx-icon rain", children=[
            html.Div(className="cloud-bubble b1"),
            html.Div(className="cloud-bubble b2"),
            html.Div(className="cloud-bubble b3"),
            html.Span(className="drop d1"),
            html.Span(className="drop d2"),
            html.Span(className="drop d3"),
        ])
    ])

# ----- Layout -----
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

    # Shared data store
    dcc.Store(id="wx-data"),

    # Icon + current card
    html.Div(id="weather-icon", style={"margin": "6px 0 12px"}),
    html.Div(id="GetWeather", className="main-card"),

    # Map instead of the daily chart
    dcc.Graph(id="place-map", figure={"data": [], "layout": {"title": "Location Map"}}),

    # Keep hourly chart + small summary
    dcc.Graph(id="hourly-chart", figure={"data": [], "layout": {"title": "Hourly Temperature"}}),
    html.Div(id="summary-table", style={"maxWidth": "680px", "margin": "10px auto"}),

    # 7-day cards strip
    html.Div(id="forecast-cards", style={"display": "flex", "overflowX": "auto", "padding": "10px"})
])

# =========================================================
# Callback 1: Fetch data once and put in Store (Open-Meteo)
# =========================================================
@callback(
    Output("wx-data", "data"),
    Input("inputCity", "value"),
    Input("inputCountry", "value"),
    Input("TempSetting", "value"),
)
def fetch_weather(city, country, tempUnit):
    try:
        # Geocode
        location = placeFinder.geocode({"city": city, "country": country}, timeout=10)
        if not location:
            return {"error": "Location not found."}
        lat, lon = float(location.latitude), float(location.longitude)
        resolved_place = location.address
        lat_str, lon_str = f"{lat:.3f}", f"{lon:.3f}"

        # Units
        temp_unit = "fahrenheit" if str(tempUnit).lower().startswith("f") else "celsius"
        unit_symbol = "°F" if temp_unit == "fahrenheit" else "°C"

        # API call
        api_params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "temperature_unit": temp_unit,
            "hourly": ["temperature_2m", "precipitation", "relative_humidity_2m"],
            "past_days": 3,
            "forecast_days": 4,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        }
        response = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=api_params)[0]

        # Hourly
        hourly = response.Hourly()
        t_start = pd.to_datetime(hourly.Time(),    unit="s", utc=True)
        t_end   = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True)
        step    = pd.Timedelta(seconds=hourly.Interval())
        dt_idx  = pd.date_range(start=t_start, end=t_end, freq=step, inclusive="left")

        local_tz  = dt_idx.tz
        now_local = pd.Timestamp.now(tz=local_tz)
        diff_secs = ((dt_idx - now_local) / pd.Timedelta(seconds=1)).astype(float)
        idx_now   = int(np.argmin(np.abs(diff_secs)))

        hourly_times_local = dt_idx.tz_convert(None).strftime("%Y-%m-%d %H:%M").tolist()
        hourly_temp   = hourly.Variables(0).ValuesAsNumpy().tolist()
        hourly_precip = hourly.Variables(1).ValuesAsNumpy().tolist()
        hourly_humid  = hourly.Variables(2).ValuesAsNumpy().tolist()

        # Daily
        daily  = response.Daily()
        d_start = pd.to_datetime(daily.Time(),    unit="s", utc=True)
        d_end   = pd.to_datetime(daily.TimeEnd(), unit="s", utc=True)
        d_step  = pd.Timedelta(seconds=daily.Interval())
        d_idx   = pd.date_range(start=d_start, end=d_end, freq=d_step, inclusive="left").tz_convert(local_tz)

        today   = pd.Timestamp.now(tz=local_tz).normalize()
        offsets = ((d_idx.normalize() - today).days).tolist()

        daily_dates = d_idx.tz_convert(None).strftime("%Y-%m-%d").tolist()
        daily_tmax  = daily.Variables(0).ValuesAsNumpy().tolist()
        daily_tmin  = daily.Variables(1).ValuesAsNumpy().tolist()
        daily_rain  = daily.Variables(2).ValuesAsNumpy().tolist()  # mm/day

        return {
            "meta": {
                "place": resolved_place,
                "lat": lat_str,
                "lon": lon_str,
                "unit_symbol": unit_symbol,
                "temp_unit": temp_unit,
            },
            "hourly": {
                "times": hourly_times_local,
                "temperature": hourly_temp,
                "precip": hourly_precip,
                "humidity": hourly_humid,
                "idx_now": idx_now,
            },
            "daily": {
                "dates": daily_dates,
                "tmax": daily_tmax,
                "tmin": daily_tmin,
                "precip_sum_mm": daily_rain,
                "offsets": offsets,
            }
        }
    except Exception as e:
        return {"error": str(e)}

# ===================================================================
# Callback 2: Current card + animated icon + 7 daily "Day -3..+3" cards
# ===================================================================
@callback(
    Output("GetWeather", "children"),
    Output("forecast-cards", "children"),
    Output("weather-icon", "children"),
    Input("wx-data", "data"),
    Input("paramSettings", "value"),
    prevent_initial_call=False
)
def render_current_and_cards(data, params):
    if not data or "error" in data:
        msg = data.get("error", "No data") if isinstance(data, dict) else "No data"
        return html.Div(f"Error: {msg}", className="main-card"), [], html.Div()

    meta = data["meta"]
    H = data["hourly"]

    idx = max(0, min(int(H["idx_now"]), len(H["times"]) - 1))
    temp   = float(H["temperature"][idx])
    humid  = float(H["humidity"][idx])
    precip = float(H["precip"][idx])
    time_str = H["times"][idx]
    unit_symbol = meta["unit_symbol"]

    # Icon + background class
    if precip > 0.2:
        bg_class, icon = "rainy", rain_icon()
    elif humid >= 70:
        bg_class, icon = "cloudy", cloud_icon()
    else:
        bg_class, icon = "clear", sun_icon()

    rain_now_txt = f"{precip/25.4:.2f} in" if meta["temp_unit"] == "fahrenheit" else f"{precip:.2f} mm"

    pieces = [
        html.H2("Current conditions"),
        html.Small(f"{meta['place']} • ({meta['lat']}, {meta['lon']})"),
        html.P(f"Time: {time_str}")
    ]
    if "Temperature" in params: pieces.append(html.P(f"Temperature: {temp:.1f}{unit_symbol}"))
    if "Humidity"   in params: pieces.append(html.P(f"Humidity: {humid:.0f}%"))
    if "Rain"       in params: pieces.append(html.P(f"Rain: {rain_now_txt}"))

    main_card = html.Div(className=f"main-card {bg_class}", children=pieces)

    # 7 daily cards (Day -3..+3)
    D = data["daily"]
    cards = []
    for date_str, tmax, tmin, rain_mm, off in zip(D["dates"], D["tmax"], D["tmin"], D["precip_sum_mm"], D["offsets"]):
        if -3 <= int(off) <= 3:
            rain_txt = f"{float(rain_mm)/25.4:.2f} in" if meta["temp_unit"] == "fahrenheit" else f"{float(rain_mm):.2f} mm"
            cards.append(
                html.Div(className="card", children=[
                    html.P(f"Day {int(off):+d}".replace("+", "")),
                    html.P(f"High: {float(tmax):.0f}{unit_symbol} • Low: {float(tmin):.0f}{unit_symbol}"),
                    html.P(f"Rain: {rain_txt}")
                ])
            )

    return main_card, cards, icon

# ===============================
# Callback 3: Hourly Temp Plot
# ===============================
@callback(
    Output("hourly-chart", "figure"),
    Input("wx-data", "data"),
    prevent_initial_call=False
)
def render_hourly_chart(data):
    if not data or "error" in data:
        return {"data": [], "layout": {"title": "Hourly Temperature"}}

    H = data["hourly"]
    unit = data["meta"]["unit_symbol"]

    fig = {
        "data": [{
            "x": H["times"],
            "y": H["temperature"],
            "mode": "lines",
            "name": f"Temperature ({unit})",
            "hovertemplate": "%{x}<br>%{y:.1f} " + unit + "<extra></extra>",
        }],
        "layout": {
            "title": "Hourly Temperature (recent → near future)",
            "xaxis": {"title": "Local time"},
            "yaxis": {"title": unit},
            "margin": {"l": 40, "r": 10, "t": 50, "b": 40},
        },
    }
    return fig

# ===============================
# Callback 4: Location Map (NEW)
# ===============================
@callback(
    Output("place-map", "figure"),
    Input("wx-data", "data"),
    prevent_initial_call=False
)
def render_map(data):
    if not data or "error" in data:
        return {"data": [], "layout": {"title": "Location Map"}}

    meta = data["meta"]
    H = data["hourly"]
    idx = max(0, min(int(H["idx_now"]), len(H["times"]) - 1))

    # Build hover text using the "now" reading
    unit = meta["unit_symbol"]
    temp = float(H["temperature"][idx])
    humid = float(H["humidity"][idx])
    precip = float(H["precip"][idx])
    rain_txt = f"{precip/25.4:.2f} in" if meta["temp_unit"] == "fahrenheit" else f"{precip:.2f} mm"

    hover = (f"<b>{meta['place']}</b><br>"
             f"Lat/Lon: {meta['lat']}, {meta['lon']}<br>"
             f"Temp: {temp:.1f}{unit}<br>"
             f"Humidity: {humid:.0f}%<br>"
             f"Precip: {rain_txt}")

    fig = go.Figure(go.Scattermapbox(
        lat=[float(meta["lat"])],
        lon=[float(meta["lon"])],
        mode="markers",
        marker={"size": 18},
        hovertemplate=hover + "<extra></extra>",
        name="Location"
    ))

    fig.update_layout(
        title="Location Map",
        mapbox={
            "style": "open-street-map",
            "center": {"lat": float(meta["lat"]), "lon": float(meta["lon"])},
            "zoom": 9
        },
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        height=420,
        showlegend=False
    )
    return fig

# =================================
# Callback 5: Small summary table
# =================================
@callback(
    Output("summary-table", "children"),
    Input("wx-data", "data"),
    prevent_initial_call=False
)
def render_summary_table(data):
    if not data or "error" in data:
        return html.Div("No summary available.")

    meta = data["meta"]
    H = data["hourly"]
    idx = max(0, min(int(H["idx_now"]), len(H["times"]) - 1))

    temp = float(H["temperature"][idx])
    humid = float(H["humidity"][idx])
    precip = float(H["precip"][idx])
    unit = meta["unit_symbol"]
    rain_txt = f"{precip/25.4:.2f} in" if meta["temp_unit"] == "fahrenheit" else f"{precip:.2f} mm"

    return html.Table(
        className="table table-sm table-striped",
        children=[
            html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td("Location"), html.Td(f"{meta['place']} ({meta['lat']}, {meta['lon']})")]),
                html.Tr([html.Td("Now – Temperature"), html.Td(f"{temp:.1f}{unit}")]),
                html.Tr([html.Td("Now – Humidity"), html.Td(f"{humid:.0f}%")]),
                html.Tr([html.Td("Now – Precip"), html.Td(rain_txt)]),
            ])
        ]
    )
=======
from dash import html, dcc, register_page

# Weather Info page (placeholder UX ready for your callbacks)
register_page(__name__, path="/page1", name="Weather Info")

layout = html.Div(
    className="container",
    children=[
        html.H2("Weather Info"),
        html.P("Select a city and view the next 48 hours of temperatures (coming next)."),

        # Controls (IDs ready for callbacks you’ll add later)
        html.Div(
            className="mb-3",
            children=[
                html.Label("City"),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=[
                        {"label": "New York", "value": "new_york"},
                        {"label": "San Francisco", "value": "san_francisco"},
                        {"label": "Miami", "value": "miami"},
                    ],
                    value="new_york",
                    clearable=False,
                ),
            ],
        ),

        html.Div(
            className="mb-3",
            children=[
                html.Button("Refresh", id="refresh-btn", className="btn btn-secondary"),
            ],
        ),

        # Chart placeholder
        dcc.Loading(
            type="default",
            children=dcc.Graph(id="temp-chart", figure={"data": [], "layout": {"title": "Temperature (next 48h)"}})
        ),

        # KPIs placeholders
        html.Div(
            className="row mt-4",
            children=[
                html.Div(className="col-md-4", children=[html.H4(id="kpi-now", children="Now: — °C")]),
                html.Div(className="col-md-4", children=[html.H4(id="kpi-min", children="Min: — °C")]),
                html.Div(className="col-md-4", children=[html.H4(id="kpi-max", children="Max: — °C")]),
            ],
        ),

        # Simple table placeholder
        html.Div(className="mt-4", children=[html.Div(id="summary-table")]),
    ],
)
>>>>>>> Stashed changes
