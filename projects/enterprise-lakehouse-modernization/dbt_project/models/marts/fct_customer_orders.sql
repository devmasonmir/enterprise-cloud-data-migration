{{ config(materialized='table') }}

with silver_orders as (
    select
        customer_id,
        cast(amount as decimal(18, 2)) as amount,
        cast(event_time as timestamp) as event_time
    from {{ source('lakehouse', 'silver_orders') }}
)
select
    customer_id,
    count(*) as order_count,
    sum(amount) as total_amount,
    max(event_time) as last_order_at
from silver_orders
group by customer_id
