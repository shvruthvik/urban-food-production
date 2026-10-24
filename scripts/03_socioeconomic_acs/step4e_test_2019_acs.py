
import requests
from getpass import getpass

api_key = getpass("Enter your replacement Census API key: ")

url = "https://api.census.gov/data/2019/acs/acs5"

tracts_to_test = [
    ("20", "091", "051802", "Johnson County, Kansas"),
    ("20", "209", "040300", "Wyandotte County, Kansas"),
    ("29", "095", "000300", "Jackson County, Missouri"),
]

for state, county, tract, county_name in tracts_to_test:

    params = {
        "get": "NAME,B01003_001E,B19013_001E",
        "for": f"tract:{tract}",
        "in": f"state:{state} county:{county}",
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=30)

    print("\n" + "=" * 50)
    print(county_name)
    print("Testing tract:", state + county + tract)
    print("Status code:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        if len(data) > 1:
            print("Tract found:", data[1])
        else:
            print("No tract record returned.")
    else:
        print("Response:", response.text)
