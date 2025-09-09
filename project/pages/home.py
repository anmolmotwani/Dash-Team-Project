import dash
from dash import html, dcc

dash.register_page(__name__, path="/")

layout = html.Div(
    className="homePage clear",
    children=[
        html.H1("Welcome to Weather Report 🌤️"),
        html.P("Type a city on the Weather Report page to see 7 days past & future weather."),
        
        # Button that navigates to the Weather Report page
        html.Div(
            dcc.Link(
                "Go to Weather",
                href="/weather",
                className="btn btn-primary btn-lg"  # Bootstrap-styled button
            ),
            className="mt-3"
        ),
    ]
)
