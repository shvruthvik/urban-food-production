
import requests
import pandas as pd
from getpass import getpass

# Enter your Census API key privately
api_key = 'e1aea9cb2af00120982d9931cd8a6877cd146ae2'

url = "https://api.census.gov/data/2023/acs/acs5"

params = {
    "get": "NAME,B01003_001E,B19013_001E",
    "for": "tract:*",
    "in": "state:29 county:095",
    "key": api_key
}

response = requests.get(url, params=params, timeout=30)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    print("Number of tracts returned:", len(df))
    print(df.head(5).to_string(index=False))
else:
    print("Response:", response.text)