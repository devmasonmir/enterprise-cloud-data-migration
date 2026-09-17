from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'mason-mir',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'enterprise_cloud_migration_orchestrator',
    default_args=default_args,
    description='Batch incremental migration from Teradata/SAP to AWS Lakehouse',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    t_extract = BashOperator(task_id='extract_incremental_delta', bash_command='echo "Extracting delta..."')
    t_glue = BashOperator(task_id='trigger_aws_glue_job', bash_command='echo "Running Glue job..."')
    t_dbt = BashOperator(task_id='run_dbt_marts', bash_command='cd dbt_project && dbt run')
    t_audit = BashOperator(task_id='execute_reconciliation_audit', bash_command='echo "Auditing reconciliation..."')
    t_extract >> t_glue >> t_dbt >> t_audit
