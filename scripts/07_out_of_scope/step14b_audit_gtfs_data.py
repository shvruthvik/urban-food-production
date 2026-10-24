
from pathlib import Path
from zipfile import ZipFile
import pandas as pd

gtfs_file = Path("data/kcata_gtfs_october2026_20261001.zip")

with ZipFile(gtfs_file, "r") as archive:

    # Read the tables directly from the ZIP
    agency = pd.read_csv(archive.open("agency.txt"), dtype=str)
    routes = pd.read_csv(archive.open("routes.txt"), dtype=str)
    stops = pd.read_csv(archive.open("stops.txt"), dtype=str)
    trips = pd.read_csv(archive.open("trips.txt"), dtype=str)
    stop_times = pd.read_csv(
        archive.open("stop_times.txt"), dtype=str
    )

    print("1. AGENCY INFORMATION")
    print(agency.to_string(index=False))

    print("\n2. FEED INFORMATION")
    try:
        feed_info = pd.read_csv(
            archive.open("feed_info.txt"), dtype=str
        )
        print(feed_info.to_string(index=False))
    except Exception as error:
        print("Could not read feed_info:", error)

    print("\n3. ROUTE SUMMARY")
    print("Total routes:", len(routes))
    print("Route types:")
    print(routes["route_type"].value_counts(dropna=False).to_string())

    route_names = [
        col for col in ["route_short_name", "route_long_name"]
        if col in routes.columns
    ]
    print("\nRoute names:")
    print(routes[route_names].to_string(index=False))

    print("\n4. STOP SUMMARY")
    print("Total stop records:", len(stops))
    print("Unique stop IDs:", stops["stop_id"].nunique())

    stops["stop_lat"] = pd.to_numeric(
        stops["stop_lat"], errors="coerce"
    )
    stops["stop_lon"] = pd.to_numeric(
        stops["stop_lon"], errors="coerce"
    )

    valid_stops = stops.dropna(subset=["stop_lat", "stop_lon"])

    print("Stops with valid coordinates:", len(valid_stops))

    if len(valid_stops) > 0:
        print("Latitude range:",
              valid_stops["stop_lat"].min(),
              "to", valid_stops["stop_lat"].max())
        print("Longitude range:",
              valid_stops["stop_lon"].min(),
              "to", valid_stops["stop_lon"].max())

    print("\n5. SERVICE DATE RANGE")
    try:
        calendar = pd.read_csv(
            archive.open("calendar.txt"), dtype=str
        )
        print("Calendar start dates:",
              calendar["start_date"].min())
        print("Calendar end dates:",
              calendar["end_date"].max())
        print("Calendar service records:", len(calendar))
    except Exception as error:
        print("Could not read calendar:", error)

    try:
        calendar_dates = pd.read_csv(
            archive.open("calendar_dates.txt"), dtype=str
        )
        print("Calendar exception records:", len(calendar_dates))
        print("Exception date range:",
              calendar_dates["date"].min(),
              "to", calendar_dates["date"].max())
    except Exception as error:
        print("Could not read calendar_dates:", error)

    print("\n6. TRIP AND STOP-TIME SUMMARY")
    print("Trip records:", len(trips))
    print("Unique trip IDs:", trips["trip_id"].nunique())
    print("Stop-time records:", len(stop_times))

    print("\n7. STOP COORDINATE SAMPLE")
    print(valid_stops[["stop_name", "stop_lat", "stop_lon"]]
          .head(5).to_string(index=False))

print("\nGTFS audit complete. ZIP file was not modified.")
