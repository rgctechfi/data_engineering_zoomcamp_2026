# Flow: 04_postgres_taxi

## Description
The CSV Data used in the course: https://github.com/DataTalksClub/nyc-tlc-data/releases

## Inputs
- **taxi**: Select taxi type (yellow or green). Default: `yellow`.
- **year**: Select year (2019 or 2020). Default: `2019`.
- **month**: Select month (01 to 12). Default: `01`.

## Variables
- **file**: Constructed filename based on inputs (e.g., `yellow_tripdata_2019-01.csv`).
- **staging_table**: `public.<taxi>_tripdata_staging`
- **table**: `public.<taxi>_tripdata`
- **data**: Path to the extracted CSV file.

## Tasks

### 1. set_label
Sets execution labels:
- `file`: The filename being processed.
- `taxi`: The taxi type.

### 2. extract
Downloads the compressed CSV file from GitHub and unzips it using `gunzip`.

### 3. if_yellow_taxi / if_green_taxi
Based on the selected `taxi` input, the flow executes the corresponding block of tasks.

#### Yellow Taxi Steps:
1. **yellow_create_table**: Creates the main table `public.yellow_tripdata` if it doesn't exist.
2. **yellow_create_staging_table**: Creates the staging table `public.yellow_tripdata_staging` if it doesn't exist.
3. **yellow_truncate_staging_table**: Truncates the staging table to clear old data.
4. **yellow_copy_in_to_staging_table**: Copies data from the downloaded CSV into the staging table.
5. **yellow_add_unique_id_and_filename**:
   - Generates a `unique_row_id` using MD5 hash of key columns.
   - Adds the `filename` to each record.
6. **yellow_merge_data**: Merges data from staging to the main table. New records are inserted based on `unique_row_id`.

#### Green Taxi Steps:
1. **green_create_table**: Creates the main table `public.green_tripdata` if it doesn't exist.
2. **green_create_staging_table**: Creates the staging table `public.green_tripdata_staging` if it doesn't exist.
3. **green_truncate_staging_table**: Truncates the staging table.
4. **green_copy_in_to_staging_table**: Copies data from CSV to staging table.
5. **green_add_unique_id_and_filename**:
   - Generates a `unique_row_id`.
   - Adds the `filename`.
6. **green_merge_data**: Merges data from staging to the main table.

### 4. purge_files
Removes the current execution files to clean up storage.

## Plugin Defaults
- **PostgreSQL**: Configured to connect to `jdbc:postgresql://pgdatabase:5432/ny_taxi` with user `root` and password `root`.
