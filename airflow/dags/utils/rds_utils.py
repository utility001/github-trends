import logging

from airflow.models import Variable
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

def connect_to_rds():
    """
    Creates a SQLAlchemy engine for RDS using Airflow Variables
    """
    db_username = Variable.get("RDS_DB_USERNAME")
    db_password = Variable.get("RDS_DB_PASSWORD")
    db_host = Variable.get("RDS_DB_HOST")  # aka Endpoint in AWS console
    db_port = Variable.get("RDS_DB_PORT", default_var=5432)
    db_name = Variable.get("RDS_DB_NAME", default_var="githubtrends")

    connection_string = (
        f"postgresql+psycopg2://{db_username}:"
        f"{db_password}@{db_host}:{db_port}/{db_name}"
    )
    return create_engine(connection_string)


def check_table_existence_on_rds() -> bool:
    print("Connecting to database")
    engine = connect_to_rds()

    logger.info(f"Checking for 'public.trending_repos' table")
    check_table_sql = """SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'trending_repos'
        );"""
    with engine.connect() as conn:
        result = conn.execute(text(check_table_sql))
        exists = result.scalar()
        logger.info(f"public.trending_repos  exists? - {exists}")
    return exists


def create_table_on_rds():
    create_table_sql = text(
        f"""
        CREATE TABLE public.trending_repos(
        repo_id BIGINT NOT NULL,
        repo_name TEXT NOT NULL,
        repo_full_name TEXT,
        description TEXT,
        primary_language TEXT,
        no_of_stars BIGINT,
        no_of_forks BIGINT,
        no_of_watchers BIGINT,
        no_of_open_issues BIGINT,
        repo_created_at TIMESTAMPTZ,
        repo_updated_at TIMESTAMPTZ,
        repo_pushed_at TIMESTAMPTZ,
        default_branch_name TEXT,
        ssh_url TEXT NOT NULL,
        clone_url TEXT NOT NULL,
        homepage TEXT,
        size_of_repo BIGINT NOT NULL,
        license TEXT,
        query_date DATE NOT NULL,
        PRIMARY KEY(repo_id, query_date)
        );
        """
    )

    engine = connect_to_rds()
    print(f"creating table public.trending_repos")
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(create_table_sql)
            # conn.commit()
    logger.info(f"Table public.trending_repos created Successfully")


def insert_into_rds(db_engine: Engine, data: list[dict]) -> None:
    """
    Inserts cryptocurrency data into RDS postgres database
    """
    total_records = len(data)
    logger.info(f"Inserting {total_records} records into RDS")

    insert_sql = text(
        f"""
        INSERT INTO public.trending_repos(
            repo_id, repo_name, repo_full_name,
            description, primary_language, no_of_stars,
            no_of_forks, no_of_watchers, no_of_open_issues,
            repo_created_at, repo_updated_at, repo_pushed_at,
            default_branch_name, ssh_url, clone_url,
            homepage, size_of_repo, license, query_date
        ) VALUES (
            :repo_id, :repo_name, :repo_full_name,
            :description, :primary_language, :no_of_stars,
            :no_of_forks, :no_of_watchers, :no_of_open_issues,
            :repo_created_at, :repo_updated_at, :repo_pushed_at,
            :default_branch_name, :ssh_url, :clone_url,
            :homepage, :size_of_repo, :license, :query_date
        )"""
    )

    with db_engine.connect() as conn:
        with conn.begin():
            conn.execute(insert_sql, data)
            # conn.commit()

    logger.info("Insert Operation Completed Successfully")
