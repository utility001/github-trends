FROM apache/airflow:2.10.5

WORKDIR /app

COPY requirements.txt /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

USER airflow