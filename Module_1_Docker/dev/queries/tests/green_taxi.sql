SELECT COUNT(trip_distance)
FROM green_taxi_data
WHERE lpep_pickup_datetime BETWEEN '2025-11-01%' AND '2025-12-01%'
AND trip_distance <= 1