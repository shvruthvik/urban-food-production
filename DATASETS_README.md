# Dataset inventory and acquisition guide

## Important
The GitHub repository intentionally excludes `data/raw/` and some large root-level source files. Raw data should be stored locally under `data/raw/` using the folder structure below. Do not upload API keys, credentials, or restricted data. Keep the original project copy and source downloads as backups.

The source files listed below reflect the project work and available notes. Check current official download pages and release versions before replacing an existing source.

## 1. CDC PLACES health data
Suggested local folder: `data/raw/health/`

Relevant source:
- CDC PLACES Census Tract Data (GIS-Friendly Format), 2023 release, dated in filename `20260112`.
- The project has used the tract-level PLACES data and derived `_CrudePrev` measures.
- Prefer the tract-level GIS-friendly CSV for tract analysis. Place-level and ZCTA-level PLACES files are separate geographies and are not interchangeable with tract-level data.

Official source portal:
https://www.cdc.gov/places/

The project previously used files with names similar to:
- `PLACES__Census_Tract_Data_(GIS_Friendly_Format),_2023_release_20260112.csv`
- `PLACES__Local_Data_for_Better_Health,_Census_Tract_Data_2023_release_20260112.csv`
- `PLACES__Local_Data_for_Better_Health,_Place_Data_2023_release_20260112.csv`
- `PLACES__ZCTA_Data_(GIS_Friendly_Format),_2023_release_20260112.csv`

Only obtain the files needed for the script being run; do not assume place/ZCTA data can replace tract data.

## 2. American Community Survey (ACS) socioeconomic data
Suggested local folder: `data/raw/socioeconomic/`

The project uses 2019 ACS 5-year estimates for the Kansas City metro study tracts. The candidate table used by the project is named:
- `acs_2019_kc_metro_candidate_data.csv`

Related expected/intermediate files may include:
- `acs_2019_candidate_diagnostic.csv`
- `acs_2019_kc_metro_cleaned.csv`

These are project-generated/intermediate tables, not necessarily files to download directly. Some scripts query the Census API; others expect the saved CSVs to exist. Official source:
https://data.census.gov/
Census API documentation:
https://www.census.gov/data/developers/data-sets/acs-5year.html

Use the same ACS vintage and variable definitions as the project if reproducing prior results. A Census API key may be needed for API access.

## 3. USDA Food Access / Atlas and related food-access sources
Suggested local folder: `data/raw/food_access/`

The project contains 2019 food-access analysis notes and summaries, including LRAM/SRAM-related comparisons and geography diagnostics. Obtain the exact source files referenced by the original scripts/notes before rerunning food-access integration. Do not substitute a newer release without documenting the vintage change.

USDA Food Access Research Atlas:
https://www.ers.usda.gov/data-products/food-access-research-atlas/

Geography caveat: the 2019 Atlas uses older census-tract geography. Project checks matched 430 of 516 study tracts when comparing with 2020 tract identifiers; harmonization is needed before final integration.

## 4. Census tract boundaries and tract crosswalks
Suggested local folder: `data/raw/geography/`

The project scripts refer to Census tract boundary files, state/county geography, and 2010-to-2020 tract relationship/crosswalk data. Keep boundary vintage consistent with the tract IDs used in each source. Official source:
https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

Large boundary ZIPs and shapefile components were intentionally omitted from GitHub. Preserve each shapefile's related `.shp`, `.shx`, `.dbf`, `.prj`, and other sidecar files together.

## 5. Parcel / land availability data
Suggested local folder: `data/raw/built_environment/`

The project currently includes candidate-parcel analysis for Kansas City, Missouri. Related processed outputs include:
- `data/processed/built_environment/kcmo_vacant_candidate_parcels.csv`
- `data/processed/built_environment/kcmo_vacant_candidate_parcels.geojson`
- `data/processed/built_environment/kcmo_candidates_in_study_area.geojson`
- `outputs/parcels/`

The Missouri parcel source was a local/source dataset, not a standard nationwide download. Obtain the corresponding parcel data from the appropriate official local government GIS/open-data source and document the download date, license, and land-use definitions. Kansas parcel data has not been fully integrated; the current parcel results should not be interpreted as complete metro-wide land availability.

## 6. Large source files and archive
The original working folder contained large source data and a `data.zip` archive. These were not uploaded to GitHub. If the instructor needs the raw data, share it separately through the course-approved storage location or provide official source links. Do not assume the GitHub repository alone is a complete raw-data package.

## Recommended local folder layout
```text
data/
  raw/
    health/
    socioeconomic/
    food_access/
    geography/
    built_environment/
  processed/
    health/
    socioeconomic/
    food_access/
    geography/
    built_environment/
    integrated/
```

## Before running any script
1. Read the script's input/output paths.
2. Confirm the expected file exists in the indicated folder.
3. Check the source vintage and geographic identifiers.
4. Back up any existing output the script might overwrite.
5. Do not run download or data-regeneration scripts unless you intend to refresh those datasets.
