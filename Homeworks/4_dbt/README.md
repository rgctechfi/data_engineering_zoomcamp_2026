Voici la page complète en markdown avec les images dans le bon ordre. Vous pouvez copier ce contenu pour l'exporter :

---

# NYC Taxi Data Warehousing Analysis

## Setup

### Dataset Information

- **Period**: January 2024 - June 2024
- **Data Source**: NYC Yellow Taxi Trip Records (Parquet format)
- **Storage**: .parquet and .db
- **Analysis Platform**: DuckDB

---

# Module 4 — Analytics Engineering (dbt) — Homework

## Setup

- **Repo**: dbt project for NYC taxi transformations
- **Data**: Green & Yellow taxi (2019–2020) — load into your warehouse
- **Run**: `dbt build --target prod`

```bash
OUTPUT:
07:23:09  Running with dbt=1.10.19
07:23:09  Registered adapter: duckdb=1.10.0
07:23:10  Found 3 models, 2 sources, 472 macros
07:23:10  
07:23:10  Concurrency: 1 threads (target='prod')
07:23:10  
07:23:10  1 of 3 START sql view model prod.stg_green_tripdata ............................ [RUN]
07:23:10  1 of 3 OK created sql view model prod.stg_green_tripdata ....................... [OK in 0.07s]
07:23:10  2 of 3 START sql view model prod.stg_yellow_tripdata ........................... [RUN]
07:23:10  2 of 3 OK created sql view model prod.stg_yellow_tripdata ...................... [OK in 0.03s]
07:23:10  3 of 3 START sql view model prod.int_trips_unioned ............................. [RUN]
07:23:10  3 of 3 OK created sql view model prod.int_trips_unioned ........................ [OK in 0.02s]
07:23:10  
07:23:10  Finished running 3 view models in 0 hours 0 minutes and 0.27 seconds (0.27s).
07:23:10  
07:23:10  Completed successfully
07:23:10  
07:23:10  Done. PASS=3 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=3
```

# <b> OUT OF MEMORY FIX : using a batch logical to iterate dbt run on each month of 2019 and 2020
Final database size: 25.25 GB
</b>

All the datas inside database duckdb(local):
```sql
SELECT extract(year from pickup_datetime) AS annee, count(*) FROM prod.fct_trips GROUP BY 1 ORDER BY 1;"
┌───────┬──────────────┐
│ annee │ count_star() │
│ int64 │    int64     │
├───────┼──────────────┤
│  2019 │     87373242 │
│  2020 │     24493276 │
```
---

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


Selected answer:

<b>
In dbt, the --select flag is very specific about what it executes based on the syntax you use:

dbt run --select model_name: Runs ONLY that specific model. It ignores parents and children.

dbt run --select +model_name: Runs the model AND all its parents (upstream dependencies).

dbt run --select model_name+: Runs the model AND all its children (downstream dependencies).

Since your command is just int_trips_unioned without any + signs, dbt will isolate that single node in the DAG (Direct Acyclic Graph) and build only that one table.
</b>

<p align="center">
  <img src="https://img.shields.io/badge/Answer-`int_trips_unioned` only-53cf74" alt="Answer Q1">
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

Selected answer:

<p align="center">
  <img src="https://img.shields.io/badge/Answer-dbt will fail the test, returning a non‑zero exit code-53cf74" alt="Answer Q2">
</p>

<b>
The test in dbt is a SQL query that checks all rows where payment_type IS NOT IN the list [1, 2, 3, 4, 5]. The verdict of the test is if this query returns at least one row (in our case, those with the value 6), dbt considers it as a failed test.

The system impact: A failing dbt test raises an error (red in the terminal) and returns a non-zero exit code. This allows to stop automated deployment pipelines (CI/CD) to avoid pushing corrupted data into production.
</b>


---

### Question 3. Counting Records in `fct_monthly_zone_revenue`

What is the record count in the `fct_monthly_zone_revenue` model?

Selected answer:

```sql
duckdb data/database/taxi_rides_ny.duckdb "SELECT count(*) FROM prod.fct_monthly_zone_revenue;"

┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│    11812     │
└──────────────┘
```
Not the same value for me.

```sql
duckdb data/database/taxi_rides_ny.duckdb "SELECT count(distinct revenue_month) FROM prod.fct_monthly_zone_revenue;"

┌───────────────────────────────┐
│ count(DISTINCT revenue_month) │
│             int64             │
├───────────────────────────────┤
│              24               │
└───────────────────────────────┘
```
I have all the months inside

<p align="center">
  <img src="https://img.shields.io/badge/Answer-12,184-53cf74" alt="Answer Q3">
</p>

---

### Question 4. Best Performing Zone for Green Taxis (2020)

Which pickup zone has the highest `revenue_monthly_total_amount` for Green taxis in 2020?

- East Harlem North
- Morningside Heights
- East Harlem South
- Washington Heights South

Selected answer:

```sql
duckdb data/database/taxi_rides_ny.duckdb "
SELECT 
    pickup_zone, 
    sum(revenue_monthly_total_amount) as total_revenue
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND extract(year from revenue_month) = 2020
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 1;"

    pickup_zone    │ total_revenue │
│      varchar      │ decimal(38,3) │
├───────────────────┼───────────────┤
│ East Harlem North │  1814667.640 
```
<p align="center">
  <img src="https://img.shields.io/badge/Answer-East Harlem North-53cf74" alt="Answer Q4">
</p>

---

### Question 5. Green Taxi Trip Counts (October 2019)

Total `total_monthly_trips` for Green taxis in October 2019:

- 500,234
- 350,891
- 384,624
- 421,509

Selected answer:

```sql
duckdb data/database/taxi_rides_ny.duckdb "
SELECT 
    service_type,
    sum(total_monthly_trips) as total_trips
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND extract(year from revenue_month) = 2019
  AND extract(month from revenue_month) = 10
GROUP BY 1;"

  │ service_type │ total_trips │
│   varchar    │   int128    │
├──────────────┼─────────────┤
│ Green        │   384624    │
 ```
<p align="center">
  <img src="https://img.shields.io/badge/Answer-384624-53cf74" alt="Answer Q5">
</p>

---

### Question 6. Build a Staging Model for FHV Data

Create `stg_fhv_tripdata` for 2019 FHV data, filter `dispatching_base_num IS NOT NULL`, and rename fields to match the project's naming conventions.

What is the record count for `stg_fhv_tripdata`?

Selected answer:

```bash
dbt run --select stg_fhv_tripdata --target prod
08:58:07  Running with dbt=1.10.19
08:58:07  Registered adapter: duckdb=1.10.0
08:58:08  Found 9 models, 2 seeds, 26 data tests, 3 sources, 618 macros
08:58:08  
08:58:08  Concurrency: 1 threads (target='prod')
08:58:08  
08:58:08  1 of 1 START sql view model prod.stg_fhv_tripdata .............................. [RUN]
08:58:08  1 of 1 OK created sql view model prod.stg_fhv_tripdata ......................... [OK in 0.06s]
08:58:08  
08:58:08  Finished running 1 view model in 0 hours 0 minutes and 0.17 seconds (0.17s).
08:58:08  
08:58:08  Completed successfully
08:58:08  
08:58:08  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=1
```
```sql
duckdb data/database/taxi_rides_ny.duckdb "SELECT count(*) FROM prod.stg_fhv_tripdata"
┌─────────────────┐
│  count_star()   │
│      int64      │
├─────────────────┤
│    43244693     │
│ (43.24 million) │
```

<p align="center">
  <img src="https://img.shields.io/badge/Answer-43,244,693-53cf74" alt="Answer Q6">
</p>

---
