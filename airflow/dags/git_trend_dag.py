# Import
import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

from utils.etl_utils import github_api_to_s3, s3_to_rds, transform_and_upload_data
from utils.rds_utils import check_table_existence_on_rds, create_table_on_rds

# DAG timezone configuration
UTC_TIMEZONE = pendulum.timezone("UTC")


def choose_path():
    """branch logic - check RDS table existence and choose next task"""

    # check if table exists on the database
    check = check_table_existence_on_rds()

    if check:
        return "skip-create-table"
    return "create-table"


# Default arguments block
default_args = {
    "owner": "Data Engineering Team",
    "retries": 2,
    "retry_delay": pendulum.duration(minutes=3),
}

# Dag definition block
dag = DAG(
    dag_id="github-trends-pipeline",
    description="Gets data from github API - tranform - Loads into RDS",
    schedule="@daily",
    start_date=pendulum.datetime(year=2025, month=8, day=1, tz=UTC_TIMEZONE),
    default_args=default_args,
    catchup=False,
)

task_1_check_table = BranchPythonOperator(
    task_id="check-table", python_callable=choose_path, dag=dag
)

task_2a_create_table = PythonOperator(
    task_id="create-table", python_callable=create_table_on_rds, dag=dag
)

task_2b_empty = EmptyOperator(task_id="skip-create-table", dag=dag)

task_3_api_to_s3 = PythonOperator(
    task_id="github-api-to-s3",  # merging point
    python_callable=github_api_to_s3,
    trigger_rule="none_failed_min_one_success",
    dag=dag,
)

task_4_transform = PythonOperator(
    task_id="s3-data-transform-and-reupload",
    python_callable=transform_and_upload_data,
    dag=dag,
)

task_5_s3_to_rds = PythonOperator(
    task_id="s3-to-rds",
    python_callable=s3_to_rds,
    dag=dag,
)

task_1_check_table >> [task_2a_create_table, task_2b_empty]
[task_2a_create_table, task_2b_empty] >> task_3_api_to_s3
task_3_api_to_s3 >> task_4_transform
task_4_transform >> task_5_s3_to_rds
