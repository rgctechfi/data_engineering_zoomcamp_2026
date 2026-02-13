Voici la page complète en markdown avec les images dans le bon ordre. Vous pouvez copier ce contenu pour l'exporter :

---

# NYC Taxi Data Warehousing Analysis

## Setup

### Dataset Information

- **Period**: January 2024 - June 2024
- **Data Source**: NYC Yellow Taxi Trip Records (Parquet format)
- **Storage**: GCS Bucket
- **Analysis Platform**: BigQuery

### Infrastructure Setup

You can copy this content for export.

---

# Module 4 — Analytics Engineering (dbt) — Homework

## Setup

- **Repo**: dbt project for NYC taxi transformations
- **Data**: Green & Yellow taxi (2019–2020) — load into your warehouse
- **Run**: `dbt build --target prod`

---

## Context

This README is a formatted version of `homework_dbt.md`. Questions and choices are listed below. To make colored text display correctly on GitHub, I replaced inline HTML styles with Shields.io badges — they render colors reliably in GitHub Markdown.

> Example badge (replace "TBD" with your answer):

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-5bde7e" alt="Answer">
</p>

## Questions & Choices

### Question 1. dbt Lineage and Execution

Given structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/
    └── int_trips_unioned.sql (depends on stg_green_tripdata & stg_yellow_tripdata)
```

What will `dbt run --select int_trips_unioned` build?

- `stg_green_tripdata`, `stg_yellow_tripdata`, and `int_trips_unioned` (upstream deps)
- Any model with upstream and downstream dependencies related to `int_trips_unioned`
- `int_trips_unioned` only
- `int_trips_unioned`, `int_trips`, and `fct_trips` (downstream deps)

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q1">
</p>

---

### Question 2. dbt Tests

Generic test in `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

If a new value `6` appears in the source data, what happens when running `dbt test --select fct_trips`?

- dbt will skip the test because the model didn't change
- dbt will fail the test, returning a non‑zero exit code
- dbt will pass the test with a warning
- dbt will update the configuration to include the new value

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q2">
</p>

---

### Question 3. Counting Records in `fct_monthly_zone_revenue`

What is the record count in the `fct_monthly_zone_revenue` model?

- 12,998
- 14,120
- 12,184
- 15,421

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q3">
</p>

---

### Question 4. Best Performing Zone for Green Taxis (2020)

Which pickup zone has the highest `revenue_monthly_total_amount` for Green taxis in 2020?

- East Harlem North
- Morningside Heights
- East Harlem South
- Washington Heights South

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q4">
</p>

---

### Question 5. Green Taxi Trip Counts (October 2019)

Total `total_monthly_trips` for Green taxis in October 2019:

- 500,234
- 350,891
- 384,624
- 421,509

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q5">
</p>

---

### Question 6. Build a Staging Model for FHV Data

Create `stg_fhv_tripdata` for 2019 FHV data, filter `dispatching_base_num IS NOT NULL`, and rename fields to match the project's naming conventions.

What is the record count for `stg_fhv_tripdata`?

- 42,084,899
- 43,244,693
- 22,998,722
- 44,112,187

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-TBD-lightgrey" alt="Answer Q6">
</p>

---

## Notes on color display in GitHub

- GitHub sanitizes most inline `style` attributes in Markdown, so inline color styling (e.g. `<div style="color:#...">`) is often removed.
- Recommended solution: use Shields.io badges or hosted SVG images. Badges are quick and reliably render colors on GitHub.
- To change a badge color, replace `TBD` and `lightgrey` in the badge URL:

```
https://img.shields.io/badge/Answer-VALUE-<color>
```

Valid color examples: `brightgreen`, `green`, `yellow`, `orange`, `red`, `blue`, `lightgrey`.

---

If you want me to fill the badges with the correct answers (green for chosen answers, grey for others), tell me which choices to mark and I'll update the file.

Would you like me to populate answers and add short explanations for each question?

Si vous voulez que je remplisse les badges avec les réponses correctes (ou vos choix), dites‑moi lesquelles et je mettrai à jour les badges en vert pour les réponses choisies et en gris pour les non‑sélectionnées.

Bon travail — voulez‑vous que je remplisse les réponses et ajoute des explications pour chaque question ?