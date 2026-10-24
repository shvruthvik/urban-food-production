# Urban Food Production Suitability Analysis — Project Review Guide

## 1. Project Overview

This project explores data preparation and candidate-variable screening for an urban food production suitability analysis in the Kansas City metropolitan area. The working study geography contains **516 census tracts across 14 counties**.

This guide identifies selected scripts and existing outputs that can help a reviewer examine the work completed so far. It distinguishes reviewing existing results from rerunning analyses.

**Current status:** Health and socioeconomic screening, food-access investigation, and Kansas City, Missouri parcel analysis have produced intermediate outputs. Final AHP/MCDA suitability scoring, scenario comparisons, Priority Stability analysis, and the ArcGIS Online dashboard remain future work.

## 2. Current Scope and Limitations

- Health and socioeconomic data preparation, variable screening, and several geography checks have been performed.
- The USDA 2019 Food Access Research Atlas uses older census-tract geography. Approximately 430 of the 516 project tracts matched the project’s tract identifiers. Geographic harmonization remains unresolved.
- Current candidate-parcel analysis covers Kansas City, Missouri. Kansas parcel coverage is incomplete.
- Parcel land-use codes are used to identify candidates for further investigation; they do not confirm actual food-production suitability.
- Some files are intermediate diagnostic outputs. Their existence does not establish that the variables, methodology, or final suitability model have been finalized.
- Raw source data and large archives are not all included in the GitHub repository.

## 3. Repository Structure

- `scripts/01_project_setup/` — project setup, geography inspection, and source checks.
- `scripts/02_health/` — health-variable screening, correlations, candidate comparisons, and descriptive summaries.
- `scripts/03_socioeconomic_acs/` — ACS data preparation and integration.
- `scripts/04_food_access_usda/` — food-access integration and geography checks.
- `scripts/05_built_environment_parcels/` — parcel inventory, quality checks, candidate filtering, tract assignment, and summaries.
- `scripts/06_shared_geography/` — tract geography and crosswalk checks.
- `scripts/07_out_of_scope/` — exploratory transit scripts outside the core workflow.
- `data/processed/` — selected derived datasets and intermediate outputs.
- `outputs/` — parcel reports, summaries, and diagnostic tables.
- `datasets/` — dataset inventory and acquisition guidance.

## 4. Recommended Review Order

**Start by reviewing existing outputs.** This is the safest way to examine the current project without depending on external data, API access, or the ability to reproduce every intermediate step.

### 4.1 Health-variable screening

Recommended outputs:

- `data/processed/health/health_variable_quality.csv`
- `data/processed/health/health_variable_correlations_verified.csv`
- `data/processed/health/health_candidate_comparison.csv`
- `data/processed/health/health_candidate_correlations.csv`
- `data/processed/health/health_sensitivity_summary.csv`
- `data/processed/health/health_sensitivity_correlations.csv`

Relevant scripts:

| Script | Purpose |
|---|---|
| `scripts/02_health/step6l_create_full_health_screening_dataset.py` | Creates the health-variable dataset from PLACES source data |
| `scripts/02_health/step6e_verify_health_correlations.py` | Checks correlations using the prepared health dataset |
| `scripts/02_health/step6i_compare_health_candidates.py` | Compares six candidate health indicators |
| `scripts/02_health/step6j_health_sensitivity.py` | Summarizes five candidate indicators and their correlations |
| `scripts/02_health/step6c_health_variable_screening.py` | Performs initial quality checks and correlation analysis |

Important cautions:

- `step6l_create_full_health_screening_dataset.py` requires the raw PLACES tract dataset.
- `step6e`, `step6i`, and `step6j` depend on `data/processed/health/kc_metro_health_all_variables.csv`.
- `step6c_health_variable_screening.py` and `step6d_health_variable_correlations.py` both write `health_variable_correlations.csv`. Running them can replace the same output.
- `step6j_health_sensitivity.py` produces descriptive statistics and correlations. Its output should not be described as a completed weight-sensitivity experiment.
- `step6k_health_variable_screening_report.py` has input paths that differ from the locations in the current output inventory. Inspect its paths before running it.

### 4.2 ACS download, audit, cleaning, and integration

Recommended existing outputs:

- `data/raw/socioeconomic/acs_2019_kc_metro_candidate_data.csv`
- `data/raw/socioeconomic/acs_2019_audit_report.csv`
- `data/raw/socioeconomic/acs_2019_kc_metro_cleaned.csv`
- `data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`
- `data/processed/integrated/kc_metro_variable_summary.csv`

#### ACS download

Script:

`scripts/03_socioeconomic_acs/step4f_download_2019_acs_data.py`

Input:

`data/processed/integrated/kc_metro_tract_data.csv`

Output:

`data/raw/socioeconomic/acs_2019_kc_metro_candidate_data.csv`

This script requests 2019 ACS 5-year estimates for Kansas and Missouri through the Census API, filters the results to the project tract IDs, calculates candidate percentages, and writes a candidate dataset.

**Prerequisites:** Internet access, the required Python packages, the existing PLACES tract dataset, and a valid Census API key.

The script prompts for the key using `getpass`; do not paste a working key into this guide or into public documentation. Check the printed matched and unmatched tract counts before relying on a newly generated dataset.

#### ACS audit

Script:

`scripts/03_socioeconomic_acs/step4g_audit_acs_data.py`

Input:

`data/raw/socioeconomic/acs_2019_kc_metro_candidate_data.csv`

Output:

`data/raw/socioeconomic/acs_2019_audit_report.csv`

The script prints row counts, unique tracts, missing-value details, negative ACS estimates, and percentage summaries. The saved CSV contains missing-value counts by column; the other checks are printed to the terminal.

Rerunning it overwrites the audit report.

#### ACS cleaning

Script:

`scripts/03_socioeconomic_acs/step4i_clean_acs_data.py`

Input:

`data/raw/socioeconomic/acs_2019_candidate_diagnostic.csv`

Output:

`data/raw/socioeconomic/acs_2019_kc_metro_cleaned.csv`

This script converts estimate fields to numeric values, replaces a Census sentinel value with missing data, calculates selected socioeconomic percentages, prints quality summaries, and saves the cleaned dataset.

**Workflow caution:** The cleaning script reads `acs_2019_candidate_diagnostic.csv`, while the download script writes `acs_2019_kc_metro_candidate_data.csv`. The diagnostic file exists in the current working repository, but its generation process has not yet been verified as part of this review. Do not assume the download script automatically produces the cleaning script’s input.

Rerunning the cleaning script overwrites the cleaned ACS dataset.

#### Health and ACS integration

Script:

`scripts/03_socioeconomic_acs/step5_combine_health_acs.py`

Inputs:

- `data/processed/integrated/kc_metro_tract_data.csv`
- `data/raw/socioeconomic/acs_2019_kc_metro_cleaned.csv`

Output:

`data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`

The script standardizes tract IDs, selects the candidate ACS indicators, merges them with the existing tract-level data, and reports merge validation statistics.

Related validation script:

`scripts/03_socioeconomic_acs/step5a_validate_combined_data.py`

Input:

`data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`

Output:

`data/processed/integrated/kc_metro_combined_missing_values.csv`

The validation script reports row counts, unique and duplicate tract IDs, selected descriptive statistics, and missing-value counts. It can overwrite the missing-value output.

Related variable summary script:

`scripts/03_socioeconomic_acs/step6b_create_variable_summary.py`

Input:

`data/processed/integrated/kc_metro_combined_health_socioeconomic.csv`

Output:

`data/processed/integrated/kc_metro_variable_summary.csv`

This output summarizes selected candidate health and socioeconomic variables. The variables and their roles remain preliminary rather than final AHP criteria.

### 4.3 USDA food-access integration

Existing integrated dataset:

`data/processed/integrated/kc_metro_combined_health_socioeconomic_LRAM2019.csv`

Script:

`scripts/04_food_access_usda/step_usda_lram2019_integration.py`

The script selects seven USDA 2019 food-access indicators and attempts to merge them with the existing health and socioeconomic dataset.

**Important limitations:**

- Only approximately 430 of the 516 project tracts matched the older USDA tract identifiers in the current geography comparison.
- The script’s input and output paths require verification against the current repository layout.
- Its validation can stop processing when unmatched tracts remain, before writing the expected outputs.
- The existing integrated dataset is available for inspection, but its presence does not prove that the current script will reproduce it successfully.
- Matching tract identifiers alone does not establish that the source geometries are equivalent.

Review the existing integrated file before attempting a rerun. Geographic harmonization must be addressed before treating the USDA indicators as final suitability criteria.

### 4.4 Parcel data quality and candidate screening

Current parcel analysis covers Kansas City, Missouri source parcels only.

Recommended existing outputs:

- `outputs/parcels/parcel_layer_inventory.txt`
- `outputs/parcels/parcel_field_inventory.csv`
- `outputs/parcels/parcel_sample_100.csv`
- `outputs/parcels/parcel_landuse_code_counts.csv`
- `outputs/parcels/parcel_data_quality_by_field.csv`
- `outputs/parcels/parcel_quality_summary.csv`
- `outputs/parcels/candidate_landuse_summary.csv`

Relevant scripts:

| Script | Purpose | Main output |
|---|---|---|
| `scripts/05_built_environment_parcels/inspect_parcel_data.py` | Inspects source layers and fields | `outputs/parcels/parcel_layer_inventory.txt` and related inventory files |
| `scripts/05_built_environment_parcels/analyze_parcel_quality.py` | Checks parcel attributes, identifiers, geometry, and land-use codes | Quality summary and field-quality tables |
| `scripts/05_built_environment_parcels/summarize_candidate_parcels.py` | Compares five possible land-use codes | `outputs/parcels/candidate_landuse_summary.csv` |
| `scripts/05_built_environment_parcels/filter_candidate_parcels.py` | Extracts land-use codes 9500 and 9600 | Candidate parcel CSV and GeoJSON |
| `scripts/05_built_environment_parcels/check_parcel_coverage.py` | Selects candidates intersecting the study area | `data/processed/built_environment/kcmo_candidates_in_study_area.geojson` |

Candidate outputs:

- `data/processed/built_environment/kcmo_vacant_candidate_parcels.csv`
- `data/processed/built_environment/kcmo_vacant_candidate_parcels.geojson`
- `data/processed/built_environment/kcmo_candidates_in_study_area.geojson`

The parcel candidate filters use land-use codes 9500 (vacant residential) and 9600 (vacant non-residential). The summary script compares these with other land-use codes, including agricultural, horticultural, and permanent open space.

These are screening categories, not confirmed suitable sites. The current process does not establish all zoning, ownership, contamination, access, or operational constraints. Intersecting the study area also does not mean that an entire parcel is inside the boundary.

### 4.5 Parcel-to-tract assignment and integration

Relevant scripts:

| Script | Purpose | Main output |
|---|---|---|
| `scripts/05_built_environment_parcels/assign_parcels_to_tracts.py` | Assigns candidate parcels to tracts using representative points | Assignment, count, and unassigned-parcel CSVs |
| `scripts/05_built_environment_parcels/merge_parcels_with_tract_data.py` | Merges parcel counts with the integrated tract dataset | `data/processed/integrated/kc_metro_health_socioeconomic_parcel_counts.csv` |

Existing outputs:

- `outputs/parcels/candidate_parcel_tract_assignments.csv`
- `outputs/parcels/candidate_parcel_counts_by_tract.csv`
- `outputs/parcels/unassigned_candidate_parcels.csv`
- `data/processed/integrated/kc_metro_health_socioeconomic_parcel_counts.csv`

The assignment script uses parcel representative points and a spatial join to assign parcels to census tracts. The count CSV includes tracts with assigned candidates; tracts with zero candidates may be absent from that intermediate file.

The integration script starts from the tract-level health, socioeconomic, and USDA dataset, merges parcel counts, and fills missing parcel counts with zero. It checks for duplicate tract IDs in the parcel-count input and uses a one-to-one merge.

The resulting file is the current integrated tract-level output. Before interpreting zeros, confirm that missing parcel counts represent no assigned candidates rather than an incomplete parcel-processing step.

## 5. KCMO Parcel Archive

The source archive `Cadastre.gdb.zip` is large and is not included in the GitHub repository.

**Shared download link:** `[https://wichitaedu-my.sharepoint.com/:f:/g/personal/y247k345_wichita_edu/IgDjglFU1LqDSb1IFPbA448RAWdxPLuoilKnEuvinxHrhaA?e=yAKkT4]`

After obtaining the archive:

1. Download `Cadastre.gdb.zip` from the shared location.
2. Place it in the Windows Downloads folder.
3. Confirm that the filename and path match the relevant script's configuration.
4. Inspect whether a script reads the ZIP directly or expects extracted files.
5. Confirm all required inputs and output paths before running the script.
6. Back up important outputs before rerunning any step that may overwrite them.

The parcel source-inspection and quality-analysis scripts use the Downloads-folder archive path. Other parcel scripts use project-relative paths and previously generated parcel outputs. Verify these settings before attempting to reproduce the workflow on another computer.

To check the expected archive location, run:

```powershell
Test-Path "$HOME\Downloads\Cadastre.gdb.zip"
Get-Item "$HOME\Downloads\Cadastre.gdb.zip" |
    Select-Object Name, Length, LastWriteTime
```

The first command should return `True` if the archive exists at that location.

## 6. API Keys and Online Services

Some ACS scripts access the U.S. Census Bureau API. The API test script is:

`scripts/03_socioeconomic_acs/test_acs_api.py`

The download script `step4f_download_2019_acs_data.py` prompts for a Census API key when run. Do not publish working API keys, passwords, or credentials in a public repository or in this guide.

No completed ArcGIS Online dashboard or dashboard credentials are included in the current review package.

## 7. Existing Outputs Versus Reproducibility

The following files have been confirmed to exist in the current local working repository:

**Health:**
- `health_variable_quality.csv`
- `health_variable_correlations_verified.csv`
- `health_candidate_comparison.csv`
- `health_sensitivity_summary.csv`

**ACS and integration:**
- `acs_2019_kc_metro_candidate_data.csv`
- `acs_2019_audit_report.csv`
- `acs_2019_candidate_diagnostic.csv`
- `acs_2019_kc_metro_cleaned.csv`
- `kc_metro_combined_health_socioeconomic.csv`
- `kc_metro_variable_summary.csv`

**Food access and integrated data:**
- `kc_metro_combined_health_socioeconomic_LRAM2019.csv`
- `kc_metro_health_socioeconomic_parcel_counts.csv`

**Parcel analysis:**
- `kcmo_vacant_candidate_parcels.csv`
- `kcmo_vacant_candidate_parcels.geojson`
- `kcmo_candidates_in_study_area.geojson`
- `parcel_quality_summary.csv`
- `candidate_landuse_summary.csv`
- `candidate_parcel_tract_assignments.csv`
- `candidate_parcel_counts_by_tract.csv`
- `unassigned_candidate_parcels.csv`

These existence checks do not independently validate file contents or guarantee that the current scripts can reproduce every file. Some scripts depend on raw data, API access, earlier intermediate files, or path configurations that require verification.

For review, start with the existing outputs and inspect the corresponding script. Rerun an individual script only after confirming its prerequisites and overwrite behavior.

## 8. Work Remaining

The following tasks remain before the project can be considered a complete suitability analysis:

- Complete geographic harmonization for USDA food-access indicators.
- Integrate parcel coverage for the Kansas side of the metropolitan area.
- Finalize the health and socioeconomic variables and their methodological justification.
- Complete the AHP/MCDA suitability scoring methodology.
- Implement and compare scenarios, including Score Change, Rank Change, and Priority Stability.
- Complete the ArcGIS Online dashboard.
- Verify the reproducibility of the selected scripts and their expected outputs.

## 9. Reproducibility and Data Safety

- Review a script's inputs, outputs, dependencies, and side effects before running it.
- Confirm that required raw and intermediate files exist.
- Preserve important outputs before rerunning scripts that write to the same location.
- Do not run every script blindly; some are exploratory, some require external data, and some may overwrite files.
- Check each result before proceeding to a dependent step.
- Keep API keys, credentials, and restricted data out of public documentation and commits.

This guide describes the current project state and selected review artifacts. It is not a guarantee that the entire workflow can be reproduced without additional data, path verification, and validation.
