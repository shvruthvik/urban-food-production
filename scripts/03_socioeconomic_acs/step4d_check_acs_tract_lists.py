
import requests
from getpass import getpass

api_key = getpass("Enter your replacement Census API key: ")

url = "https://api.census.gov/data/2023/acs/acs5"

counties_to_check = [
    ("20", "091", "Johnson County, Kansas", "20091051802"),
    ("20", "209", "Wyandotte County, Kansas", "20209040300"),
]

for state, county, county_name, target_id in counties_to_check:

    params = {
        "get": "NAME",
        "for": "tract:*",
        "in": f"state:{state} county:{county}",
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=60)

    print("\n" + "=" * 50)
    print(county_name)
    print("Status code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        headers = data[0]
        rows = data[1:]

        tract_index = headers.index("tract")
        found_ids = [
            state + county + row[tract_index]
            for row in rows
        ]

        print("ACS tracts returned:", len(found_ids))
        print("Target PLACES ID:", target_id)

        if target_id in found_ids:
            print("RESULT: Target ID exists in the ACS tract list.")
        else:
            print("RESULT: Target ID does not exist in the ACS tract list.")

        print("\nFirst 10 ACS tract IDs:")
        print(found_ids[:10])

    else:
        print("Response:", response.text)

