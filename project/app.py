from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
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

    
