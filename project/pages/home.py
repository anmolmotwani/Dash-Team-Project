import dash
from dash import html, dcc

dash.register_page(__name__,path="/")

layout = html.Div([
    ##Find out something interesting to put on the home page.
    
    html.H2("Welcome to our Weather Report"),
    dcc.Markdown(id = "WR", children = '''
                 Are you looking for the jazz fusion band [Weather Report](https://youtu.be/SvhmaNlLgRM?si=1hyegq2V5DvHG-fH)?
                 ''')
    
    ##We could possibly have the homepage display specifically Williamsburg
    
],className="homePage"
                  )