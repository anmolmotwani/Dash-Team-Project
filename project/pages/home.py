import dash
from dash import html

dash.register_page(__name__,path="/")

layout = html.Div([
    ##Find out something interesting to put on the home page.
    html.H2("Welcome to our Weather Report"),
    html.A("For the Band Weather Report, click here.", href = "https://youtube.com/playlist?list=PLP1lC0FnuI0K26N-Z_CtZmaP36Mg5NBdO&si=QeXag6kVPEZDrk9M")
])