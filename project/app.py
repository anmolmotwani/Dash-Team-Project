from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
<<<<<<< Updated upstream
    suppress_callback_exceptions=True,
    title="Weather App",
    external_stylesheets=[dbc.themes.BOOTSTRAP],  # keep your current theme
)
server = app.server

app.layout = html.Div([
    dbc.NavbarSimple(
        id="main-navbar",
        brand="Weather Report",
        brand_href="/",
        children=[
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Weather Report", href="/weather", active="exact"),
        ],
        dark=True,                   # light text
        color=None,                  # disable contextual color so custom bg shows
        style={"backgroundColor": "#073642"},  # exact match to your card color
        className="mb-0",
    ),
    page_container
])

if __name__ == "__main__":
    app.run(debug=True)

    
=======
    external_stylesheets=[dbc.themes.SOLAR],   # Bootswatch Solar
    suppress_callback_exceptions=True,         # needed for multi-page
)
server = app.server

navbar = dbc.NavbarSimple(
    brand="Weather Report",
    brand_href="/",
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Weather Info", href="/page1", active="exact")),
    ],
    color="dark",
    dark=True,
    className="mb-3",
)

app.layout = html.Div(
    children=[
        navbar,
        page_container,   # renders current page from /pages
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
>>>>>>> Stashed changes
