{{ config(materialized='table') }}

WITH fact_sales AS (
    SELECT 
        transaction_id,
        customer_id,
        product_id,
        transaction_date,
        product_name,
        product_price,
        product_quantity,
        total_amount
    FROM {{ source('postgres', 'transaction') }}
)

SELECT DISTINCT
    fs.transaction_id,
    fs.customer_id,
    fs.product_id,
    d.sales_date,
    fs.product_name AS phone_name,
    fs.product_price  AS phone_price,
    fs.product_quantity as phones_sold,
    fs.total_amount
FROM fact_sales fs
INNER JOIN {{ ref('dim_dates') }} d ON fs.transaction_id = d.transaction_id
INNER JOIN {{ ref('dim_customers') }} c ON fs.customer_id = c.customer_id
INNER JOIN {{ ref('dim_products') }} p ON fs.product_id = p.product_id
