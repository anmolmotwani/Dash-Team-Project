##Not sure if this works the way i think its gonna work but here goes

from geopy.geocoders import Nominatim

place_finder = Nominatim(user_agent = "my_user_agent")

#result = place_finder.geocode("Berlin", addressdetails=True)
#print(f"Latitude: {result.latitude} \nLongitude: {result.longitude}")
#cityTest = input("Put in a city: ")
#result = place_finder.geocode(cityTest, addressdetails=True)
#print(f"Latitude: {result.latitude} \nLongitude: {result.longitude}")

##We could try llimiting the scope to only the US?

def getLatLong (cityX, countryY):
    ##if we want to restrict to only USA we could add country_codes=us
    cityLatLong = place_finder.geocode({'city':cityX, 'country':countryY}, addressdetails=True)
    return(cityLatLong.latitude, cityLatLong.longitude)

x = input("City: ")
y = input("Country: ")
print(getLatLong(x,y))