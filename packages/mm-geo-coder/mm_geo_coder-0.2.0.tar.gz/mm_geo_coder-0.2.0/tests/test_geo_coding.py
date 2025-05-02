from mm_geo_coder.geocoder import MMGeoCoder

def test_geocoding_address_in_mimu():
    address = "ပျဥ်းမနားမြို့ ၊ မင်္ဂလာရပ်ကွက် မြန်မာနိုင်ငံ"
    geo_coder = MMGeoCoder(address)
    location = geo_coder.get_geolocation()

    assert location is not None, "Location should not be None"
    assert isinstance(location, list) and len(location) > 0, "Location should be a non-empty list"

    first_result = location[0]

    expected_address = "မင်္ဂလာရပ်ကွက်၊ ပျဉ်းမနား၊ ဒက္ခိဏခရိုင်၊ နေပြည်တော်"
    expected_pcode = "MMR018006701505"
    expected_latitude = 19.7367158
    expected_longitude = 96.2005628

    assert first_result['address'] == expected_address, f"Expected address '{expected_address}', but got '{first_result['address']}'"
    assert abs(first_result['latitude'] - expected_latitude) < 1e-5, f"Latitude mismatch: {first_result['latitude']}"
    assert abs(first_result['longitude'] - expected_longitude) < 1e-5, f"Longitude mismatch: {first_result['longitude']}"
    assert first_result['pcode'] == expected_pcode, f"PCode mismatch: {first_result['pcode']}"


def test_reverse_geocoding_in_mimu():
    latitude = 19.7367158
    longitude = 96.2005628
    geo_coder = MMGeoCoder(address=None)
    geo_coder.latitude = latitude
    geo_coder.longitude = longitude

    address = geo_coder.get_reverse()

    assert address is not None, "Address should not be None"
    assert isinstance(address, dict), "Address should be a dictionary"

    expected_address = "မင်္ဂလာရပ်ကွက်၊ ပျဉ်းမနား၊ ပျဉ်းမနား၊ ဒက္ခိဏခရိုင်၊ နေပြည်တော်"    

    assert address['address'] == expected_address, f"Expected address '{expected_address}', but got '{address['address']}'"
    
def test_geocoding_address_in_nominatim():
    address = "Yangon, Myanmar"
    geo_coder = MMGeoCoder(address)
    location = geo_coder.get_geolocation()    
    assert location is not None, "Location should not be None"

def test_geocoding_address_not_in_mimu():
    address = "Nonexistent Address, Myanmar"
    geo_coder = MMGeoCoder(address)
    location = geo_coder.get_geolocation()

    assert location is None, "Location should be None for nonexistent address"

def test_reverse_geocoding_not_in_mimu():
    latitude = 0.0
    longitude = 0.0
    geo_coder = MMGeoCoder(address=None)
    geo_coder.latitude = latitude
    geo_coder.longitude = longitude

    address = geo_coder.get_reverse()

    assert address is None, "Address should be None for nonexistent coordinates"