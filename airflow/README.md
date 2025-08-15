# Airflow - GitHub Trends Data Pipeline

This folder contains Apache Airflow DAGs and utility scripts to orchestrate the ETL pipeline.

## DAG Overview

**DAG Name:** `github-trends-pipeline`

### Workflow Steps
+ Check if tabl exists on RDS
+ Branch:
  - create table if missing
  - or skip if table already exists
+ Extract data from Github API and push to s2 bucket
+ Pull raw data from s3 bucket, transform it and push to s3 bucket
+ Pull transformed data from s3 bucket and insert into RDS

## files

| File | Description |
| - | - |
| `dags/github_trends_dag.py` | Main Airflow DAG definition |
| `dags/utils/api_utils.py` | Contains Helper functions for extracting and transforming the data gotten from the API |
| `dags/utils/rds_utils.py` | Contains Helper functions for RDS Database connection, Table creation and insert operation |
| `dags/utils/etl_utils.py` | Contains helper functions for ETL |
