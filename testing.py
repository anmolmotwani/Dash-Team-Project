##Not sure if this works the way i think its gonna work but here goes

from geopy.geocoders import Nominatim

place_finder = Nominatim(user_agent = "my_user_agent")

result = place_finder.geocode("Berlin", addressdetails=True)
print(f"Latitude: {result.latitude} \nLongitude: {result.longitude}")