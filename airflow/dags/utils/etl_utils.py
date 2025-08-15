from airflow.models import Variable

from utils.api_utils import extract_trending_repos, transform_all_records
from utils.aws_utils import get_boto3_session, push_data_to_s3, get_data_from_s3
from utils.rds_utils import connect_to_rds, insert_into_rds

# AWS Configuration
BUCKET_NAME = Variable.get(
    "AWS_BUCKET_NAME", default_var="github-trends-dataset"
)  # S3 staging bucket


def github_api_to_s3(**context):
    """
    Extract trending repositories from GitHub and push raw JSON output to S3
    """
    raw_data = extract_trending_repos()

    boto3_session = get_boto3_session()

    execution_date = context["ds"]
    raw_s3_key = f"raw/trending-repos-{execution_date}.json"

    push_data_to_s3(
        boto3_session=boto3_session,
        data=raw_data,
        bucket_name=BUCKET_NAME,
        bucket_key=raw_s3_key,
    )

    context["ti"].xcom_push(key="raw_s3_key", value=raw_s3_key)


def transform_and_upload_data(**context):
    """
    Get raw data from S3, transform it, and upload transformed data back to S3
    """
    raw_s3_key = context["ti"].xcom_pull(
        task_ids="github-api-to-s3", key="raw_s3_key"
    )

    boto3_session = get_boto3_session()

    raw_data = get_data_from_s3(
        boto3_session=boto3_session,
        bucket_name=BUCKET_NAME,
        bucket_key=raw_s3_key,
    )

    transformed_data = transform_all_records(api_response=raw_data)

    execution_date = context["ds"]
    transformed_s3_key = f"transformed/trending-repos-{execution_date}.json"

    push_data_to_s3(
        boto3_session=boto3_session,
        data=transformed_data,
        bucket_name=BUCKET_NAME,
        bucket_key=transformed_s3_key,
    )

    context["ti"].xcom_push(key="transformed_s3_key", value=transformed_s3_key)


def s3_to_rds(**context):
    """Get transformed data from S3 and insert it into RDS"""

    transformed_s3_key = context["ti"].xcom_pull(
        task_ids="s3-data-transform-and-reupload", key="transformed_s3_key"
    )

    boto3_session = get_boto3_session()

    transformed_data = get_data_from_s3(
        boto3_session=boto3_session,
        bucket_name=BUCKET_NAME,
        bucket_key=transformed_s3_key,
    )

    rds_engine = connect_to_rds()

    insert_into_rds(db_engine=rds_engine, data=transformed_data)
