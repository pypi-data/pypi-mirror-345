from .mimu_database import MimuDatabase
from .nominatim import Nominatim
from .geocoder_utils import clean_address

class MMGeoCoder:
    def __init__(self, address, limit=1):
        self.address = address
        self.limit = limit
        self.mimu_db = MimuDatabase()
        self.nominatim = Nominatim()

    def get_geolocation(self):        
        location = self.mimu_db.search_in_mimu(self.address, self.limit)       
        if location:
            return location
        
        print(f"Location not found in Mimu database, searching using OpenStree API for address: {self.address}")
        cleaned_address = clean_address(self.address)  
        location = self.nominatim.search_in_nominatim(cleaned_address)
        if location:
            return location       

        
        return None
