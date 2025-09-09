from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Weather App",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Weather Report", href="/weather", active="exact")
        ],
        brand="Weather Report",
        color="primary",
        dark=True
    ),
    page_container
])

if __name__ == "__main__":
    app.run(debug=True)
