import duckdb

con = duckdb.connect('Homeworks/4_dbt/data/database/taxi_rides_ny.duckdb')

# Vérifions le nombre de colonnes dans chaque table de staging
print("Colonnes Green:", con.execute("SELECT count(*) FROM (DESCRIBE prod.stg_green_tripdata)").fetchone()[0])
print("Colonnes Yellow:", con.execute("SELECT count(*) FROM (DESCRIBE prod.stg_yellow_tripdata)").fetchone()[0])

con.close()