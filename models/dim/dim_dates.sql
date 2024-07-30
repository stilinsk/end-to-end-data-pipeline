{{ config(materialized='table') }}

WITH dim_dates AS (
    SELECT
        transaction_id,
        transaction_date,
        TO_CHAR(transaction_date, 'YYYY-MM-DD') AS sales_date
    FROM {{ source('postgres', 'transaction') }}
)

SELECT
    transaction_id,
    sales_date
FROM dim_dates
