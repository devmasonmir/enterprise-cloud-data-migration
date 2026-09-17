SELECT
    order_id,
    customer_id,
    order_amount,
    order_status,
    order_date
FROM {{ source('raw_erp', 'sap_orders') }}
WHERE order_id IS NOT NULL
