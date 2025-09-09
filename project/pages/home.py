import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div(
    className="homePage clear",
    children=[
        html.H1("Welcome to Weather Report 🌤️"),
        html.P("Type a city on the Weather Report page to see 7 days past & future weather."),
        html.P("Experience interactive cards with animated backgrounds and Apple-style design.")
    ]
)
