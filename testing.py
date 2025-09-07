##Not sure if this works the way i think its gonna work but here goes

from geopy.geocoders import Nominatim
from datetime import date


##--------------- Parameter Setting Testing

import openmeteo_requests 
from retry_requests import retry
import requests_cache 
import requests

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
urlA ="https://api.open-meteo.com/v1/forecast"

##
def initialParams():
    initParams = {
        ##Default Parameters for Williamsburg
        "latitude":37.2757,
        "longitude":76.7098,
        "hourly":["temperature_2m"],
        "past_days":5,
        "timezone" : "America/New_York" 
    }
    return (initParams)
params = initialParams()
responses = openmeteo.weather_api(urlA, params)
print(responses[0])

hourly

#-----------------Date Retrival Testing
    ###
    # today = date.today()
    # print(today)

    # today = date.today()
    # date_list = []
    # for i in range(-6,8):
    #     x = today.day + i
    #     y = today.replace(day = x)
    #     date_list.append(y)
        
    # print(date_list[0])

#-----------Place Finder Testing
    #place_finder = Nominatim(user_agent = "my_user_agent")

    #result = place_finder.geocode("Berlin", addressdetails=True)
    #print(f"Latitude: {result.latitude} \nLongitude: {result.longitude}")
    #cityTest = input("Put in a city: ")
    #result = place_finder.geocode(cityTest, addressdetails=True)
    #print(f"Latitude: {result.latitude} \nLongitude: {result.longitude}")

    ##We could try llimiting the scope to only the US?

    #def getLatLong (cityX, countryY):
        ##if we want to restrict to only USA we could add country_codes=us
        #cityLatLong = place_finder.geocode({'city':cityX, 'country':countryY}, addressdetails=True)
        #return(cityLatLong.latitude, cityLatLong.longitude)

    #x = input("City: ")
    #y = input("Country: ")
    #print(getLatLong(x,y))