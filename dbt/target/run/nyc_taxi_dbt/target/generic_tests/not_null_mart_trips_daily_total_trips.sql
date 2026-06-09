
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_trips
from `nyc-taxi-etl-498205`.`nyc_taxi`.`mart_trips_daily`
where total_trips is null



  
  
      
    ) dbt_internal_test