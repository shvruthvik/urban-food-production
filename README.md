# Urban Food Production Suitability Analysis

## Project Overview

This project explores data preparation and candidate-variable screening for an urban food production suitability analysis in the Kansas City metropolitan area. The working study geography contains **516 census tracts across 14 counties**.

The repository contains Python analysis scripts, selected processed datasets, quality-check tables, exploratory outputs, and project documentation.

**Project status:** Health and socioeconomic data preparation, food-access investigation, and Missouri-side parcel analysis have produced intermediate datasets and diagnostic outputs. Final suitability scoring and the ArcGIS Online dashboard are not yet complete.

## Current Progress

- Health-variable quality checks, correlation analysis, and candidate-variable comparisons.
- Socioeconomic data preparation using 2019 American Community Survey (ACS) 5-year estimates.
- Food-access investigation using the USDA 2019 Food Access Research Atlas.
- Census tract geography checks and cross-source integration.
- Kansas City, Missouri parcel inventory, candidate filtering, and tract assignment.
- Integration of health, socioeconomic, food-access, and parcel-count information into a tract-level dataset.

## Important Limitations

- **Parcel coverage:** Current candidate-parcel analysis covers Kansas City, Missouri. Kansas-side parcel coverage has not been fully integrated.
- **Food-access geography:** The USDA 2019 Atlas uses older census-tract geography. Approximately 430 of the 516 study tracts matched the project’s tract identifiers. Geographic harmonization remains necessary.
- **Candidate parcels:** Land-use codes are used to screen candidate parcels. They do not establish that a parcel is legally, physically, or operationally suitable for food production.
- **Suitability model:** Final AHP/MCDA scoring, scenario comparisons, Score Change, Rank Change, Priority Stability analysis, and the ArcGIS Online dashboard remain future work.
- **Data availability:** Raw data and large source files are not all included in the repository. Consult the dataset guide for acquisition instructions.

## Repository Structure

| Location | Contents |
|---|---|
| `scripts/01_project_setup/` | Project setup, geography inspection, and source checks |
| `scripts/02_health/` | Health-variable screening and comparisons |
| `scripts/03_socioeconomic_acs/` | ACS data preparation and integration |
| `scripts/04_food_access_usda/` | Food-access integration and geography checks |
| `scripts/05_built_environment_parcels/` | Parcel analysis and tract assignment |
| `scripts/06_shared_geography/` | Shared geography and crosswalk checks |
| `scripts/07_out_of_scope/` | Exploratory transit scripts outside the core workflow |
| `data/processed/` | Derived datasets and intermediate results |
| `outputs/` | Diagnostic reports, summaries, and selected outputs |
| `datasets/` | Data inventory and acquisition documentation |
| `screenshots/` | Selected screenshots |

Individual scripts have their own input and output requirements. There is no single master script that runs the entire project end to end.

## Key Outputs for Review

### Health screening

- `data/processed/health/health_variable_quality.csv`
- `data/processed/health/health_variable_correlations_verified.csv`
- `data/processed/health/health_candidate_comparison.csv`
- `data/processed/health/health_sensitivity_summary.csv`

### Socioeconomic data

- `data/raw/socioeconomic/acs_2019_kc_metro_candidate_data.csv`
- `data/raw/socioeconomic/acs_2019_audit_report.csv`
- `data/raw/socioeconomic/acs_2019_kc_metro_cleaned.csv`
- `data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`
- `data/processed/integrated/kc_metro_variable_summary.csv`

### Food-access integration

- `data/processed/integrated/kc_metro_combined_health_socioeconomic_LRAM2019.csv`

### Parcel analysis

- `data/processed/built_environment/kcmo_vacant_candidate_parcels.csv`
- `data/processed/built_environment/kcmo_vacant_candidate_parcels.geojson`
- `data/processed/built_environment/kcmo_candidates_in_study_area.geojson`
- `outputs/parcels/parcel_quality_summary.csv`
- `outputs/parcels/candidate_landuse_summary.csv`
- `outputs/parcels/candidate_parcel_tract_assignments.csv`
- `outputs/parcels/candidate_parcel_counts_by_tract.csv`
- `outputs/parcels/unassigned_candidate_parcels.csv`

### Current integrated tract-level output

`data/processed/integrated/kc_metro_health_socioeconomic_parcel_counts.csv`

This dataset brings together the current health, socioeconomic, food-access, and parcel-count information. It is an intermediate project output, not a final suitability model.

## Environment Setup

Use Python 3.11 or a compatible Python 3 version. From the repository root, run these commands in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Documentation and Review

- **[Project review guide](README_INSTRUCTOR_GUIDE.md):** Selected scripts, input/output paths, review order, prerequisites, and reproducibility cautions.
- **[Dataset inventory and acquisition guide](datasets/README.md):** Data sources, expected local folder structure, and acquisition guidance.

## Reproducibility and Data Safety

Review a script's inputs, outputs, dependencies, and side effects before running it. Some scripts access external APIs, require source data that is not included in the repository, or overwrite existing files.

Preserve important outputs before rerunning scripts, verify intermediate results before continuing, and avoid committing API keys, credentials, or restricted data.

The GitHub repository alone is not a complete raw-data package.
