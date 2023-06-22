import time

from airflow import DAG
from airflow.decorators import task
from airflow.utils.timezone import datetime


@task
def task1():
    time.sleep(10)


with DAG(
    dag_id='sleep_10',
    start_date=datetime(2021, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    task1()

