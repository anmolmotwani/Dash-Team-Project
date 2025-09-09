import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = html.Div(
    className="homePage clear",
    children=[
        html.H1("Welcome to Weather Report 🌤️"),
        html.P("Type a city on the Weather Report page to see 3 days past & future weather."),
        
        # Button that navigates to the Weather Report page
        html.Div(
            dcc.Link(
                "Go to Weather",
                href="/weather",
                className="btn btn-primary btn-lg"  # Bootstrap-styled button
            ),
            className="mt-3"
        ),
        html.Div(
            dbc.Carousel(
                items=[
                    {
                        "key": "1",
                        "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Karachi_Port_Trust_%28KPT%29_Head_Office_Building_Karachi.jpg/1920px-Karachi_Port_Trust_%28KPT%29_Head_Office_Building_Karachi.jpg",
                        "header": "Karachi, Pakistan",
                        "caption": "",
                    },
                    {
                        "key": "2",
                        "src": "https://upload.wikimedia.org/wikipedia/commons/6/68/Plaza-barrios-san-salvador.png",
                        "header": "San Salvador, El Salvador",
                        "caption": "",
                    },
                    {
                        "key": "3",
                        "src": "https://fallschurchpulse.org/wp-content/uploads/Population-growth-feature-image.jpg",
                        "header": "Falls Church, USA",
                        "caption": "",
                    },
                ],
                controls=True,
                interval = 3000,
                indicators=True,
                class_name = "carousel",
                variant='dark'
            )
        ),
    ]
)