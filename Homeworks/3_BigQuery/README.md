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

- External table from GCS bucket (Parquet files) → Google Cloud Storage
- Materialized table in BigQuery (unpartitioned, unclustered)
- Optimized table (partitioned & clustered)

---

*Context:*

I use Duckdb for exploritary data analysis : dlt_duckdb_ingesting_TESTENV.ipynb

*I use an ingesting [script.py](http://script.py) for ingesting dats to GCP Data Storage:*

datastorage_ingest_PROD

- *Don't need staging here, it's raw data and .parquet → directly on data datastorage (data lake , less cost)*
- *The script use the terrform .tfvars file as a reference for pushing the data from cloudfront to GCP in the correct project and bucket*

<div align="center">
  <img src="./3_content/image.png" width="30%">
</div>

 
## Questions & Analysis

### Question 1: Total Record Count

**Query**: Count total records for 2024 Yellow Taxi Data

```python
#With duckdb

with pipeline.sql_client() as client:
    with client.execute_query(f"SELECT count(1) FROM rides") as cursor:
        data = cursor.df()
print(data)
```
<b>
<div style="color: #5bde7e;">

**Answer Options**:

### <u>ANSWER: **20,332,093**</u>
</div>
</b>
---

### Question 2: Data Processing Estimation

**Task**: Count distinct PULocationIDs on both External Table and Materialized Table

*Since your files are in Parquet format, they already contain their own schema (column names and types). BigQuery can read it automatically! This means you don't necessarily need to list all the columns manually in the parentheses.*

## External table:

In Bigquery :

```sql
CREATE EXTERNAL TABLE `taxi-rides-ny-485214.dataset.table_name`
(
  -- optonnal for parquet !
)
OPTIONS (
  format = '...',
  uris = ['gs://taxi-rides-ny-485214-terra-bucket/raw/ny_taxi/yellow_tripdata_2024-01.parquet']
);
```

In pratice

```sql
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://taxi-rides-ny-485214-terra-bucket/raw/ny_taxi/*.parquet']
);
```
<div align="center">
  <img src="./3_content/image 1.png" width="30%">
</div>

## Materialized table:

Partition by :

```sql
CREATE OR REPLACE TABLE `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY PULocationID
AS
SELECT * FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`;
```

### **Estimated bytes processed:**

External Table : BigQuery must scan all files on Cloud Storage for each query because it does not know their content in advance. This option often scans the most data.

Native Table : BigQuery scans the entire internal table (Full Table Scan). → don't do that if you want to optimize your cost!

Partitioned Table : The best → BigQuery completely ignores days that are not in your WHERE filter. It only reads the small pieces of data that are necessary.

#### External Table:

```sql
SELECT COUNT(DISTINCT PULocationID) 
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`;
```
<div align="center">
  <img src="./3_content/image 2.png" width="30%">
</div>

BigQuery doesn't know what's in your Parquet files on GCS before actually opening them during execution. → This is why the estimate shows 0 B:

On the other hand, for the native table, BigQuery already has all the metadata internally.

#### Materialized Table:

```sql
SELECT COUNT(DISTINCT PULocationID) 
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`;
```

<div align="center">
  <img src="./3_content/image 3.png" width="30%">
</div>

<b>
<div style="color: #5bde7e;">

### <u> **Result: 0 MB / 155.12 MB** </u>

</div>
</b>


---

# **Question 3: Columnar Storage Analysis**

**Task**: Compare estimated bytes when querying one vs. two columns

**Query 1** (PULocationID only):

```sql
SELECT PULocationID
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`;
```
<div align="center">
  <img src="./3_content/image 4.png" width="30%">
</div>

**Query 2** (PULocationID + DOLocationID):

```sql
SELECT PULocationID, DOLocationID 
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`;
```
<div align="center">
  <img src="./3_content/image 5.png" width="30%">
</div>

Double the datas requierements → columnar logic

<b>
<div style="color: #5bde7e;">

### <u> **Explanation**:

ANSWER: A. \
BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed. </u>

</div>
</b>

---

### Question 4: Zero Fare Analysis

**Task**: Count records with fare_amount = 0

**Query**:

```sql
-- Zero fare query
SELECT count(fare_amount)
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`
WHERE fare_amount = 0;
```
<b>
<div style="color: #5bde7e;">

<div align="center">
  <img src="./3_content/image 6.png" width="10%">
</div>

### <u> **Result**: 8,333</u>

</div>
</b>

---

# **Question 5: Table Optimization Strategy**

**Task**: Optimize for filtering by tpep_dropoff_datetime and ordering by VendorID

**Strategy**: Partition by tpep_dropoff_datetime, Cluster on VendorID

**Rationale**:

- Partitioning on datetime reduces data scanned for date range queries
- Clustering on VendorID optimizes ORDER BY operations

**Create Optimized Table**:

```sql
-- Partitioned and clustered table creation
CREATE OR REPLACE TABLE `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`;
```

<b>
<div style="color: #5bde7e;">

### <u> **Correct Answer**: A. Partition by tpep_dropoff_datetime and Cluster on VendorID </u>

</div>
</b>
---

# **Question 6: Partitioning Performance Comparison**

**Task**: Query distinct VendorIDs between 2024-03-01 and 2024-03-15

**Query on Materialized Table**:

```sql
-- Non-partitioned table query
SELECT DISTINCT VendorID
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`
WHERE tpep_dropoff_datetime >= '2024-03-01' 
  AND tpep_dropoff_datetime <= '2024-03-15';
```
<div align="center">
  <img src="./3_content/image 7.png" width="30%">
</div>
**Query on Partitioned Table**:

```sql
-- Partitioned table query
SELECT DISTINCT VendorID
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.yellow_tripdata_partitioned`
WHERE tpep_dropoff_datetime >= '2024-03-01' 
  AND tpep_dropoff_datetime <= '2024-03-15';
```
<div align="center">
  <img src="./3_content/image 8.png" width="30%">
</div>
<b>
<div style="color: #5bde7e;">

### <u> **Result**: 310.24 MB / 26.84 MB </u>

310.24 MB (non-partitioned table → external): BigQuery had to scan the tpep_dropoff_datetime column across the entire dataset to find the rows corresponding to your period, in addition to reading the VendorID column.

26.84 MB (Partitioned table): Thanks to partition pruning, BigQuery directly "skipped" all files that did not relate to the period from 1 to 15 March. It only read the small pieces of data that were strictly necessary.

</div>
</b>
---

# **Question 7: External Table Storage Location**

<b>
<div style="color: #5bde7e;">

### <u> **Answer**: GCP Bucket</u>

External tables reference data stored in GCS without copying it into BigQuery.

</div>
</b>
---

# **Question 8: Clustering Best Practices**

<b>
<div style="color: #5bde7e;">

### <u> **Answer**: False </u>

</div>
</b>



Clustering is not always best practice. It depends on:

- Query patterns
- Data volume (effective for tables > 1GB)
- Cardinality of clustering columns
- Cost vs. performance trade-offs

---

# **Question 9 (Bonus): COUNT(*) on Materialized Table**

**Query**:

```sql
-- Count query
SELECT count(*)
FROM `taxi-rides-ny-485214.ny_taxi_bigquery_dataset.external_yellow_tripdata`
```
<div align="center">
  <img src="./3_content/image 9.png" width="30%">
</div>
<b>
<div style="color: #5bde7e;">

### <u> **Explanation**: BigQuery can retrieve COUNT(*) from table metadata without scanning actual data, resulting in 0 bytes processed.

**Here's why this happens:**

**Metadata storage: BigQuery maintains metadata about each table, including the total number of rows. This information is stored separately from the actual data.**

**No data scanning required: When you ask for COUNT(*) without any filtering conditions, BigQuery doesn't need to read through the actual table data—it simply looks up the pre-calculated row count in the metadata.**

**Cost efficiency: Since no data is scanned, you're charged 0 bytes for this type of query, making it essentially free.**

**This is different from queries with WHERE clauses or COUNT(DISTINCT column), which require scanning the actual data to filter or deduplicate values** </u>

</div>
</b>