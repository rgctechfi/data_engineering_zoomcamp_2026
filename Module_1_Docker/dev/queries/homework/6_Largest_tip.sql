SELECT 
    z."Zone" as dropoff_zone,
    MAX(g.tip_amount) as max_tip,
    g.lpep_pickup_datetime
FROM green_taxi_data g
JOIN zones z
    ON g."DOLocationID" = z."LocationID"
WHERE 
    -- 1. Filtering for the month -> extract year and month
    TO_CHAR(g.lpep_pickup_datetime, 'YYYY-MM') = '2025-11'
    
    -- 2. sub query PUlocation to text zone
    AND g."PULocationID" = (
        SELECT "LocationID" 
        FROM zones 
        WHERE "Zone" = 'East Harlem North'
    )
-- 3. GROUP BY with aggregation MAX
GROUP BY z."Zone",g. lpep_pickup_datetime
ORDER BY max_tip DESC
LIMIT 1;