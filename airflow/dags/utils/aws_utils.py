import json
import logging

import boto3
from airflow.models import Variable

logger = logging.getLogger(__name__)


def get_boto3_session():
    """Instanitiates boto3 session with credentials"""
    access_key = Variable.get("AWS_ACCESS_KEY")
    secret_key = Variable.get("AWS_SECRET_KEY")
    region_name = Variable.get("AWS_REGION", default_var="eu-north-1")

    return boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
    )


def push_data_to_s3(boto3_session, data: dict, bucket_name, bucket_key):
    """Push input python dictionary to s3 bucket as json file"""

    s3_client = boto3_session.client(service_name="s3")
    json_data = json.dumps(obj=data, default="str")

    try:
        logger.info(f"Pushing data to s3://{bucket_name}/{bucket_key}")
        s3_client.put_object(
            Bucket=bucket_name, Key=bucket_key, Body=json_data
        )
        logger.info(f"Successfully pushed data to s3://{bucket_name}/{bucket_key}")
    except Exception as e:
        logger.error(f"Push not successful: {e}")
        raise


def get_data_from_s3(boto3_session, bucket_name, bucket_key):
    """Gets Json data from s3 bucket ane returns it as a python dictionary"""

    s3_client = boto3_session.client(service_name="s3")

    try:
        logger.info(f"Getting data from s3://{bucket_name}/{bucket_key}")
        from_s3 = s3_client.get_object(Bucket=bucket_name, Key=bucket_key)

        data = from_s3["Body"].read()
        logger.info(f"Successfully pulled data from s3://{bucket_name}/{bucket_key}")

        return json.loads(data)

    except Exception as e:
        logger.exception(f"Pull not successful::: {e}")
        raise
