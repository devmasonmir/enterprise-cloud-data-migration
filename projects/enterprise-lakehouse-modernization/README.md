# Enterprise Lakehouse Modernization & Governed AI-Ready Data Products

**Resume-aligned portfolio project — synthetic example, not an employer production system.**

This project demonstrates a testable local Bronze → Silver → Gold pipeline and provides dbt modeling patterns relevant to Azure Databricks, Delta Lake, Auto Loader, PySpark, Unity Catalog, Terraform, CI/CD, and Databricks Asset Bundles experience described in Mason A. Mir's resume.

## What is implemented

- `lakehouse.py`: validate order IDs, customer IDs, amounts and timezone-aware timestamps; quarantine invalid records.
- Deduplicate order IDs by most recent ingestion timestamp **within a single batch**; report reconciliation row counts.
- Produce a customer-level Gold mart with exact Decimal currency arithmetic.
- Automated regression tests and Python 3.10/3.12 GitHub Actions checks.
- `dbt_project/`: reference SQL model and schema tests for a Databricks SQL Gold layer.

## Run the offline demo

From repository root:

```bash
cd projects/enterprise-lakehouse-modernization
python -m unittest discover -s tests -v
python lakehouse.py sample_data/orders.json
```

No credentials, cloud services, or third-party packages are needed for this local demo.

## Cloud architecture (reference, not deployed)

1. **Sources:** SQL Server, REST APIs, and cloud object storage.
2. **Bronze:** Databricks Auto Loader → Delta Lake raw ingestion with checkpoints.
3. **Silver:** PySpark validation, deduplication, schema evolution, reconciliation, and quarantine.
4. **Gold:** dbt/Databricks SQL dimensional marts and governed analytics/AI-ready inputs.
5. **Governance and delivery:** Unity Catalog access policies, Terraform, CI/CD, and Databricks Asset Bundles.

Only the local Python transformation and its tests execute in this repository. This example does not claim a live Azure deployment, Unity Catalog grants, continuous streaming, persistent Delta MERGE, Databricks Asset Bundle deployment, or production ML inference.

**Privacy:** All included orders are synthetic. Do not commit patient data, customer data, secrets, or employer code.
