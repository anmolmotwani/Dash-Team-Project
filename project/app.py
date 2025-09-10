from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title = "Weather App")
server = app.server



        
##App Layout--------------------------------------------------------------------------------------------------------------

app.layout = html.Div([
    dbc.NavbarSimple(
        children = [
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Weather Info", href="/page1", active="exact")
        ],
        brand = "Weather Report"
    ),
    page_container
])





if __name__ == "__main__":
    app.run(debug=True)
    
##very barebones layout based upon what we did in class.