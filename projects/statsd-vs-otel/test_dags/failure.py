from airflow import DAG
from airflow.decorators import task
from airflow.utils.timezone import datetime


@task
def task1():
    assert False


with DAG(
    dag_id='failing_task',
    start_date=datetime(2021, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    task1()

