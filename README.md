# GitHub Trends Data Pipeline

This is a cloud-based ETL pipline that extracts trending public repositories on Github via the [Github API](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories), stores them in AWS RDS (PostgreSQL) and syncs the data to AWs Redshift using Airbyte for the purpose of analytics   
**Orchestrated using apache airflow, provisioned with Terraform**

## Architecture

![](./images/github-trends.drawio.png)

## Tech Stack

+ Orchestration -> Apache Airflow
+ Infrastructure -> Terraform
+ Storage -> AWS RDS (PostgreSQL), AWS Redshift
+ Data Transfer -> Airbyte
+ Language -> Python3.11

## Features

+ Automated daily extraction of trending Github repositories
+ Transformation of extracted data for consistent structure
+ Infrastructure provisioning with Terraform
+ Incremental Sync from RDS to Redshift via Airbyte
+ Designed for historical trend analysis

## Project Structure

```plaintext
.
├── airflow/          # Airflow DAGs, ETL scripts, utils
│   ├── dags/
|   ├── compose.yaml
│   └── README.md
├── infrastructure/   # Terraform IaC for AWS resources
│   ├── providers.tf
│   ├── backend.tf
│   ├── variables.tf
│   ├── vpc.tf
│   ├── rds.tf
│   ├── redshift.tf
│   ├── airflow_iam.tf
│   ├── redshift_iam.tf
│   └── README.md
├── images/            # Images
└── README.md          # Documentation
```

## Getting Started

### What you need

+ AWS account with admin-level permissions
+ Terraform 
+ Python3
+ Docker - For Airflow
+ Minikube - For Airbyte

### Infrastructure Setup

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```
This provisions VPC, RDS, Redshift, IAM    
The backend state is stored in S3 bucket

---

### Airflow Setup (Docker)

+ Enter the directory
  ```bash
  cd airflow
  ```
+ Initialize airflow
  ```bash
  docker compose up airflow-init
  ```
+ Spin up the services
  ```bash
  docker compose up -d
  ```
+ Open the User Interface on `localhost:8080` and setup Variables
  ```
  RDS_DB_USERNAME
  RDS_DB_PASSWORD
  RDS_DB_HOST - (AKA Endpoint on AWS consloe)
  RDS_DB_PORT - (Default = 5432)
  RDS_DB_NAME - (Default = "github_trends") - 

  AWS_ACCESS_KEY
  AWS_SECRET_KEY
  AWS_REGION - (Default = "eu-north-1")
  ```
+ Enable `github-trends-pipeline` DAG

### Airbyte ::: RDS → Redshift

+ Source: AWS RDS (PostgreSQL)
+ Destination: AWS Redshift
+ Sync mode: Incremental + Append
+ Schedule: Every 24 hours

## Data Schema

**RDS / Redshift Table:** `public.trending_repos`

| Column | Type | Description |
| -- | - | - |
| repo_id | BIGINT | Unique repo ID from GitHub |
| repo_name | TEXT | Repository name |
| repo_full_name | TEXT | Owner/repo_name |
| description | TEXT  | Repo description (nullable) |
| primary_language | TEXT | Main programming language used |
| no_of_stars | BIGINT | Stargazer count |
| no_of_forks | BIGINT | Fork count |
| no_of_watchers | BIGINT | Watcher count |
| no_of_open_issues | SMALLINT    | Open issues count |
| repo_created_at | TIMESTAMPTZ | Creation date |
| repo_updated_at | TIMESTAMPTZ | Last updated date|
| repo_pushed_at | TIMESTAMPTZ | Last push date |
| default_branch_name | TEXT | Default branch |
| ssh_url | TEXT | SSH clone URL |
| clone_url | TEXT | HTTPS clone URL |
| homepage | TEXT | Homepage URL |
| size_of_repo | BIGINT | Repo size in bytes |
| license  | TEXT | License name |
| query_date  | DATE | Date when data was queried by the DAG |

## Use Case

Once the data has been synced to Redshift, it can be queried for::
+ Daily trending repos analysis
+ Language popularity tracking
+ Repository growth over time

## Images

### Airflow
![](./images/airflow-dag-view.png)

### Airbyte Sync
![](./images/airbyte-sync.png)

### Database
![](./images/sample-query-2.png)

---

![](./images/sample-query.png)
