--BAD version : include 12-01 day!
SELECT COUNT(trip_distance)
FROM green_taxi_data
WHERE lpep_pickup_datetime BETWEEN '2025-11-01' AND '2025-12-01'
AND trip_distance <= 1

-- BEST version : exclusive of the upper bound
SELECT COUNT(trip_distance)
FROM green_taxi_data
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;