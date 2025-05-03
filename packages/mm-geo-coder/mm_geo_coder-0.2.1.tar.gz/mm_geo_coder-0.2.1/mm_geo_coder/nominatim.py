import requests
import time

class Nominatim:
    def search_in_nominatim(self, cleaned_address):       

        location = self.get_location_from_nominatim(cleaned_address)
        
        if location:
            return {
                "address": '၊ '.join([location[0]['address'].get('road', ''), location[0]['address'].get('suburb', ''), location[0]['address'].get('city', ''), location[0]['address'].get('state', '')]),
                "latitude": location[0]['lat'],
                "longitude": location[0]['lon'],
                "pcode": location[0]['address'].get('postcode', None),
                
            }
        return None


    def get_location_from_nominatim(self, query):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json","addressdetails": 1,"limit": 1}
        headers = {"User-Agent": "MMGeoCode/1.0"}
        response = requests.get(url, params=params, headers=headers)
        time.sleep(1)  
        results = response.json()
        
        return results
    
    def search_in_nominatim_reverse(self, latitude, longitude):
        location = self.get_location_from_nominatim_reverse(latitude, longitude)        
        if location.get('error', None) is None:
            return {
            "address": location['display_name'],
            "latitude": location['lat'],
            "longitude": location['lon'],
            "pcode": location['address'].get('postcode', None),            
            }
        return None
    
    def get_location_from_nominatim_reverse(self, latitude, longitude):
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": latitude, "lon": longitude, "format": "json","addressdetails": 1,"limit": 1}
        headers = {"User-Agent": "MMGeoCode/1.0"}
        response = requests.get(url, params=params, headers=headers)
        time.sleep(1)  
        results = response.json()
        
        return results

