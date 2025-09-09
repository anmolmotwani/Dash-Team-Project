from dash import html, register_page

# Register this as the root (/) page
register_page(__name__, path="/", name="Home")

layout = html.Div(
    className="container",
    children=[
        html.H2("Home"),
        html.P("Welcome to the Weather Report demo app. Use the navbar to explore."),
        html.P(
            [
                "This app uses the ",
                html.A("Bootswatch Solar theme",
                       href="https://bootswatch.com/solar/",
                       target="_blank",
                       className="btn btn-primary"),
                " for a clean, accessible look."
            ]
        ),
    ],
)
