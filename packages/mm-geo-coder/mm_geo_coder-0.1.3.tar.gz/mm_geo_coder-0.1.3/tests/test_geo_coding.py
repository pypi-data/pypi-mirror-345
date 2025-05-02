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
