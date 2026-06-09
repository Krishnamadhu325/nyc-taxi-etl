with trips as (
    select * from `nyc-taxi-etl-498205`.`nyc_taxi`.`stg_trips`
)
select
    trip_date,
    pickup_hour,
    count(*)                                              as total_trips,
    round(avg(trip_distance), 2)                         as avg_distance_miles,
    round(avg(trip_duration_minutes), 1)                 as avg_duration_minutes,
    round(avg(total_amount), 2)                          as avg_fare_usd,
    round(sum(total_amount), 2)                          as total_revenue_usd,
    round(avg(tip_amount / nullif(fare_amount, 0)), 3)   as avg_tip_rate,
    sum(passenger_count)                                 as total_passengers
from trips
group by 1, 2
order by 1, 2