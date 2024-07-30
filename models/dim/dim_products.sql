{{ config(materialized='table') }}

with dim_products as (select * from{{source ('postgres','transaction')}})

select
transaction_id,
product_id,
product_name AS phone_name,
product_price AS phone_price,
product_quantity AS phones_sold,
payment_method

from dim_products 
