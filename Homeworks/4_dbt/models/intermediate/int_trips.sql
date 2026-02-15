{{
    config(
        materialized='incremental',
        unique_key='trip_id'
    )
}}

with unioned as (
    select * from {{ ref('int_trips_unioned') }}
),

payment_types as (
    select * from {{ ref('payment_type_lookup') }}
),

cleaned_and_enriched as (
    select
        -- Generate unique trip identifier (surrogate key pattern)
        {{ dbt_utils.generate_surrogate_key(['u.vendor_id', 'u.pickup_datetime', 'u.pickup_location_id', 'u.service_type']) }} as trip_id,

        -- Identifiers
        u.vendor_id,
        u.service_type,
        u.rate_code_id,

        -- Location IDs
        u.pickup_location_id,
        u.dropoff_location_id,

        -- Timestamps
        u.pickup_datetime,
        u.dropoff_datetime,

        -- Trip details
        u.store_and_fwd_flag,
        u.passenger_count,
        u.trip_distance,
        u.trip_type,

        -- Payment breakdown
        u.fare_amount,
        u.extra,
        u.mta_tax,
        u.tip_amount,
        u.tolls_amount,
        u.ehail_fee,
        u.improvement_surcharge,
        u.total_amount,

        -- Enrich with payment type description
        coalesce(u.payment_type, 0) as payment_type,
        coalesce(pt.description, 'Unknown') as payment_type_description

    from unioned u
    left join payment_types pt
        on coalesce(u.payment_type, 0) = pt.payment_type
)

select * from cleaned_and_enriched

-- BATCH PROCESSING
-- If we give a variable 'date_range', we will only process this month's data. Otherwise (in production run), 
-- we will process all the data, but make sure to be careful with memory usage as it can be quite large
{% if var('date_range', none) is not none %}
where pickup_datetime >= cast('{{ var("date_range") }}-01' as date)
  and pickup_datetime < cast('{{ var("date_range") }}-01' as date) + interval 1 month
{% endif %}

-- The QUALIFY statement will only run on the "small" month filtered out above
qualify row_number() over(
    partition by vendor_id, pickup_datetime, pickup_location_id, service_type
    order by dropoff_datetime
) = 1