# Urban Food Production Suitability Analysis — Instructor Guide

## Project overview
This project explores data preparation and candidate-variable screening for an urban food production suitability analysis in the Kansas City metropolitan area. The working study geography contains 516 census tracts across 14 counties.

The repository contains Python scripts, selected processed datasets, quality-check tables, exploratory outputs, maps, presentation files, and project notes. It documents work completed to date; it is **not yet a complete end-to-end suitability model or finished ArcGIS Online dashboard**.

## Important scope and limitations
- Health and socioeconomic data preparation/screening and several geography/food-access/parcel investigations have been performed.
- The final AHP/MCDA suitability scoring, scenario comparisons, Priority Stability analysis, and ArcGIS Online dashboard should be treated as future work unless separately supplied.
- The parcel candidate analysis currently covers Kansas City, Missouri source parcels only. Kansas parcel coverage is not complete, so the regional parcel picture is incomplete.
- Food-access geography requires caution: the 2019 Atlas source uses older tract geography. A comparison using 2020 tract identifiers matched 430 of 516 study tracts (about 86%); unmatched/mismatched geography needs further harmonization before using it as a final suitability criterion.
- Some processed files are intermediate diagnostic outputs. Their presence does not mean all variables have been selected or all analyses are final.
- Raw data files are intentionally not included in this GitHub repository because of size and source-data management. See `datasets/README.md` for the data inventory and acquisition guidance.

## Repository structure
- `scripts/01_project_setup/` — project setup, geography inspection, and source checks.
- `scripts/02_health/` — health-variable screening, correlation checks, candidate comparisons, and sensitivity summaries.
- `scripts/03_socioeconomic_acs/` — ACS variable selection, downloading/auditing/cleaning scripts, and integration/summary scripts.
- `scripts/04_food_access_usda/` — food-access source inspection, geography checks, candidate comparisons, and related diagnostics.
- `scripts/05_built_environment_parcels/` — parcel inventory, quality analysis, candidate filtering, tract assignment, and summaries.
- `scripts/06_shared_geography/` — tract geography and crosswalk checks.
- `scripts/07_out_of_scope/` — transit-related exploratory scripts, retained for reference and not part of the core project workflow.
- `data/processed/` — selected derived datasets and intermediate outputs included in the repository.
- `outputs/` — selected maps, reports, quality summaries, and screening results.
- `presentation scripts/` — progress presentations.
- `screenshots/` — selected screenshots.

## Environment setup
Use Python 3.11 or a compatible Python 3 version. Some geospatial dependencies can be platform-sensitive, so use a virtual environment.

From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, either allow script activation for the current user according to your institution's policy or invoke the environment's Python directly:
```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Running the project
**There is not currently a single master script that runs the entire project from raw data to final suitability scores.** Scripts are individual analysis steps and rely on specific source and intermediate files. Do not run all scripts blindly: some download data, prompt for credentials/API keys, or overwrite intermediate datasets.

Recommended approach:
1. Review the existing outputs first; they document analyses already performed.
2. Obtain and place source datasets as described in `datasets/README.md`.
3. Start with the relevant validation/inspection script for the category being reviewed.
4. Run category-specific scripts in sequence only after confirming their input files exist and their paths match the local folder.
5. Do not rerun scripts that download or regenerate key intermediate datasets unless you intend to replace those files and have backups.

### Existing output examples
Processed files include:
- `data/processed/health/health_variable_quality.csv`
- `data/processed/health/health_variable_correlations.csv`
- `data/processed/health/health_candidate_comparison.csv`
- `data/processed/health/health_sensitivity_summary.csv`
- `data/processed/health/kc_metro_health_all_variables.csv`
- `data/processed/integrated/kc_metro_tract_data.csv`
- `data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`
- `data/processed/integrated/kc_metro_variable_summary.csv`
- `data/processed/socioeconomic/acs_variable_selection_summary.csv`
- `data/processed/food_access/` — food-access inventories, merge/missingness checks, and candidate summaries
- `data/processed/geography/` — tract crosswalk and geography audit outputs
- `data/processed/built_environment/` — Missouri parcel candidates and tract-assignment outputs
- `outputs/health/`, `outputs/socioeconomic/`, `outputs/food_access/`, `outputs/geography_validation/`, and `outputs/parcels/` — selected figures, reports, and diagnostic tables

These are **existing outputs**, not a guarantee that every script can be rerun without downloading or supplying its input datasets.

## Suggested review order
1. Read `Presentation Script.md` and the most recent progress presentation.
2. Inspect `data/processed/integrated/kc_metro_variable_summary.csv`.
3. Review health screening results in `data/processed/health/`.
4. Review socioeconomic candidate selection in `data/processed/socioeconomic/` and `outputs/socioeconomic/`.
5. Review food-access geography and missingness notes in `data/processed/food_access/` and `data/processed/geography/`.
6. Review parcel coverage and candidate assignment results in `outputs/parcels/` and `data/processed/built_environment/`.
7. Check the limitations above before interpreting any result as a final suitability ranking.

## API keys and online services
Some ACS download scripts may use the Census API. A Census API key may be needed depending on the script and request limits. Do not commit API keys or credentials. No ArcGIS Online dashboard or credentials are included in this repository.

## Reproducibility note
The repository is a working research project with staged analysis scripts and intermediate results. Paths and input files should be checked before running a script. Preserve the supplied processed data and back up important outputs before rerunning any script that writes to the same location.
