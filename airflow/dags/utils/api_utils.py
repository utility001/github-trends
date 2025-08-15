import logging

import pendulum
import requests

logger = logging.getLogger(__name__)


def extract_trending_repos() -> dict:
    """Extract trending repositories from Github API"""

    URL = "https://api.github.com/search/repositories"
    PARAMS = {
        "q": "stars:>=100 created:>2024-01-01",
        "sort": "stars",
        "order": "desc",
        "per_page": 100,
    }

    logger.info("Extracting data from the API")
    response = requests.get(URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    logger.info(f"Data successfully extracted from {response.request.url}")
    return response.json()


def transform_one_record(data_dict, query_date):
    """
    Validates and extract needed fields from a single API response dictionary
    """

    license_name = None
    if data_dict.get("license") is not None:
        license_name = data_dict.get("license")["name"]

    # some homepage are just empty string, others have content, others are none
    homepage = data_dict.get("homepage", None)
    if homepage is not None and homepage.strip() == "":
        homepage = None

    needed_records = {
        "repo_id": data_dict["id"],
        "repo_name": data_dict["name"],
        "repo_full_name": data_dict["full_name"],
        "description": data_dict.get("description", None),
        "primary_language": data_dict["language"],
        "no_of_stars": data_dict["stargazers_count"],
        "no_of_forks": data_dict["forks_count"],
        "no_of_watchers": data_dict["watchers_count"],
        "no_of_open_issues": data_dict["open_issues_count"],
        "repo_created_at": data_dict["created_at"],
        "repo_updated_at": data_dict["updated_at"],
        "repo_pushed_at": data_dict["pushed_at"],
        "default_branch_name": data_dict["default_branch"],
        "ssh_url": data_dict["ssh_url"],
        "clone_url": data_dict["clone_url"],
        "homepage": homepage,
        "size_of_repo": data_dict["size"],
        "license": license_name,
        "query_date": query_date,
    }
    return needed_records


def transform_all_records(api_response: dict) -> list[dict]:
    """Transform all records from the API response into cleaned records"""

    records = api_response["items"]

    if len(records) == 0:
        logger.info("There are no records to Transform. Check the API")
        raise

    transformed_records = []

    # query date is the date that the api was queried for data
    query_date = pendulum.now("UTC").to_date_string()

    logger.info("Validating and Transforming records")
    for record in records:
        transformed_record = transform_one_record(record, query_date)
        transformed_records.append(transformed_record)

    logger.info("All Records validated and Transformed")
    return transformed_records
