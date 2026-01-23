SELECT SUM(g.total_amount) as t,
g."PULocationID",
z."Zone"
FROM green_taxi_data g
JOIN zones z
ON g."PULocationID" = z."LocationID"
WHERE DATE(lpep_pickup_datetime) = '2025-11-18'
GROUP BY "PULocationID", "Zone"
ORDER BY t DESC
LIMIT 1;