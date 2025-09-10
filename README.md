# Dash-Team-Project

<u>Project Authors:</u>

Christopher Goodwin

Anmol Matwani

Javier Cruz


<h2>Project Overview:</h2>
<h3> Problem </h3>
<p>All three members of Team 15 are from three different countries of origin. Yet all have an intrinsic need to know the weather in an easy to understand format.</p>

This project is intended as a visually clear way for anyone of even a minor level of english language skills to understand what the weather has been like and what the weather is going to be like in the coming days.

Added onto this is support for Celsius as not every location in the world uses Fahrenheit.

Data Sources:

<b>APIs and Installs Used</b>
    
    Open Meteo-Non Commercial (https://open-meteo.com/)

    Nominatim (https://github.com/osm-search/
    Nominatim)
    
    from Geopy (https://github.com/geopy/geopy)

    Dashapp, Pandas, Datetime, retry, retry_requests

<b>How to Run</b>

The app is hosted through Render servers using the dash app framework with css styling sheets and external style sheets from bootstrap.

App is to be runned from app.py, link shall appear in terminal, <i> CTRL + Click </i> the link that follows after running to host a local version of the program.

<b> AI Acnkowledgment</b>
<p>Resources such as ChatGPT and Google Gemini were used to retrieve information about resources and to check over code for bug fixing purposes. AI generated code was not used in the final product. We used AI for structuring callbacks, creating CSS animations and helped us improving our ui/uix design on home page and page 1 .</p>

<b>Data Dictionary</b>

    placeFinder: used to retrieve latitude and longitude from inputted location (Nominatim)

    response: response from the OpenMeteo API given parameters and latitude and longitude

    main_card and forecast_cards: center card and lower smaller cards that display relevant information regarding the weather.

<b>Features</b>

- Dash Pages navigation (Home and Weather Report)
- dcc.Store pattern so the API call happens once, then multiple callbacks render UI
- 4+ interactive callbacks:
   fetch data to store
   build current card + icon + daily cards
   hourly chart
   map
   summary table (extra)
- Robust time handling: selects the hourly value closest to local "now"
- CSS-animated sun, cloud, and rain icons with namespaced styles


<b>Tech Stack</b>

- Python, Dash, Plotly
- dash-bootstrap-components for layout and a carousel on Home
- geopy + Nominatim for geocoding
- open-meteo-requests for weather
- requests-cache + retry-requests for resilient API calls
- pandas and numpy for data handling



