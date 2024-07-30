{{ config(materialized='table') }}


with dim_customers as (select * from{{source('postgres','transaction')}})

select
transaction_id,
customer_id,
city,
region

from dim_customers 
