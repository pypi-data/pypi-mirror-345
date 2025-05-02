# Title
**Myanmar Address Geo Coder**

## Description

This project addresses the lack of a standardized module for Myanmar addresses and aims to make it easier for developers to retrieve the geographic coordinates of locations across Myanmar. It first searches the MIMU database to find the most precise match at the village or ward level. If a match is not found, it progressively falls back to the township, district, or region levels to provide the nearest available coordinates. If the address cannot be found in the MIMU database, the system then uses Nominatim (based on OpenStreetMap) as a fallback to retrieve the geolocation data.

### Tasks

1. **Searching the Mimu database**: Parse the given address into components (state, district, township, ward, village) and query the MIMU database for a match.
2. **Fallback to nearest available level**: If still not found, return the latitude and longitude of the nearest available administrative level (township, district, or region).
3. **Fallback to Nominatim**: If no match is found in MIMU, attempt to search using Nominatim.
4. **Return geolocation data**: Provide the best available latitude and longitude based on the search hierarchy.

---

### Installation

Install from [PyPI](https://pypi.org/project/mm-geo-coder/):

```
pip install mm_geo_coder
```
---

### Usage
```
from mm_geo_coder import MMGeoCoder

geo_coder = MMGeoCoder(address)
location = geo_coder.get_geolocation()
print(location)

```
---
## Credits and Licensing

- **Project Lead:** Myo Thida
- **Institution/Affiliation:** MMDT
- **Data Source:** Myanmar Information Management Unit (MIMU), veresion 9.6 resleased in Feb 2025

This project and its outputs are released under the **MIT License**.  
You are free to use, modify, and distribute the code and dataset with proper attribution.

> © 2025 Myo Thida. All rights reserved.  
> If you use this project in your work, please cite or link back to this repository and the parent project:  
> _"From Words to Coordinates: Mapping Myanmar's Unstructured Addresses to Coordinates."_

