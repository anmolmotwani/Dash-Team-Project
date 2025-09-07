from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc

##instantiate the app

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title = "Weather App")
