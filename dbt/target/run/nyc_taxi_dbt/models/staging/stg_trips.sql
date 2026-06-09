

  create or replace view `nyc-taxi-etl-498205`.`nyc_taxi`.`stg_trips`
  OPTIONS()
  as with source as (
    select * from `nyc-taxi-etl-498205`.`nyc_taxi`.`raw_trips`
),
renamed as (
    select
        vendorid                                                             as vendor_id,
        tpep_pickup_datetime                                                 as pickup_at,
        tpep_dropoff_datetime                                                as dropoff_at,
        passenger_count,
        trip_distance,
        pulocationid                                                         as pickup_location_id,
        dolocationid                                                         as dropoff_location_id,
        payment_type,
        fare_amount,
        tip_amount,
        tolls_amount,
        total_amount,
        congestion_surcharge,
        timestamp_diff(tpep_dropoff_datetime, tpep_pickup_datetime, minute) as trip_duration_minutes,
        extract(hour from tpep_pickup_datetime)                              as pickup_hour,
        extract(dayofweek from tpep_pickup_datetime)                        as pickup_dow,
        date(tpep_pickup_datetime)                                           as trip_date
    from source
    where tpep_pickup_datetime  is not null
      and tpep_dropoff_datetime is not null
      and trip_distance  > 0
      and fare_amount    > 0
      and total_amount   > 0
      and passenger_count between 1 and 6
)
select * from renamed;

