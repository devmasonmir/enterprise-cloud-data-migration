SELECT
    account_id,
    account_name,
    industry,
    annual_revenue,
    created_date
FROM {{ source('raw_crm', 'salesforce_accounts') }}
WHERE account_id IS NOT NULL
