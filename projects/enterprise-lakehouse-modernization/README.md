# Enterprise Lakehouse Modernization & Governed AI-Ready Data Products

An enterprise lakehouse engineering project covering Bronze/Silver/Gold data processing, validation, dimensional modeling, and cloud platform design.

## Implementation

- **Python processing:** Validates order records, normalizes identifiers, quarantines invalid data, and deduplicates by the latest ingestion timestamp within each batch.
- **Gold analytics:** Produces customer-level aggregates using decimal arithmetic and reconciliation row counts.
- **dbt:** Includes a customer-level Gold model and schema tests for Databricks SQL.
- **PySpark and Auto Loader:** Includes a Databricks ingestion and Silver transformation example in `databricks/pipeline_reference.py`.
- **Terraform:** Includes Azure Storage infrastructure definitions in `terraform/main.tf`.
- **Quality and CI:** Automated unit tests on Python 3.10 and 3.12; the Databricks example is syntax-checked.

## Run locally

```bash
cd projects/enterprise-lakehouse-modernization
python -m unittest discover -s tests -v
python lakehouse.py sample_data/orders.json
```

The local pipeline runs on synthetic records with Python's standard library. No cloud credentials are required.

## Cloud data architecture

1. Ingest SQL Server, REST API, and cloud object data into **Bronze Delta** using Databricks Auto Loader.
2. Apply **Silver** PySpark data-quality controls, schema normalization, deduplication, and source-to-target reconciliation.
3. Publish **Gold** dbt/Databricks SQL marts for analytics and feature engineering.
4. Apply **Unity Catalog** policies, observability, Terraform, and CI/CD practices for governed delivery.

**Deployment scope:** Cloud components are examples intended for configuration in an Azure/Databricks environment. This repository does not deploy a workspace or claim to provide production streaming, persistent Delta merges, Unity Catalog policy setup, or ML model serving.

**Data:** All included records are synthetic. No employer or customer data is included.
