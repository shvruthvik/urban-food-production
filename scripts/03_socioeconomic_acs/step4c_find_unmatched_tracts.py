
import requests
from getpass import getpass

# Enter your replacement Census API key privately
api_key = getpass("Enter your replacement Census API key: ")

url = "https://api.census.gov/data/2023/acs/acs5"

# Test three unmatched census tracts
tracts_to_test = [
    ("20", "091", "051802"),  # Johnson County, Kansas
    ("20", "209", "040300"),  # Wyandotte County, Kansas
    ("29", "095", "000300"),  # Jackson County, Missouri
]

for state, county, tract in tracts_to_test:

    params = {
        "get": "NAME,B01003_001E",
        "for": f"tract:{tract}",
        "in": f"state:{state} county:{county}",
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=30)

    print(f"\nTesting tract: {state}{county}{tract}")
    print("Status code:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        if len(data) > 1:
            print("Tract found:", data[1])
        else:
            print("No tract record returned.")
    elif response.status_code == 204:
        print("No data returned for this tract.")
    else:
        print("Response:", response.text)
