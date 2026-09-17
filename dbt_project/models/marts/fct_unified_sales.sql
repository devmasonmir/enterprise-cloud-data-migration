SELECT
    o.order_id,
    a.account_id,
    a.account_name,
    a.industry,
    o.order_amount,
    o.order_status,
    o.order_date
FROM {{ ref('stg_erp_orders') }} o
LEFT JOIN {{ ref('stg_salesforce_accounts') }} a
    ON o.customer_id = a.account_id
