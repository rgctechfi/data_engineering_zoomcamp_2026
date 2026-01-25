SELECT 
    trip_distance,
    lpep_pickup_datetime
FROM green_taxi_data
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1;