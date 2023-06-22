from airflow import DAG
from airflow.decorators import task
from airflow.utils.timezone import datetime


@task
def task1():
    return 'Hello'


@task
def task2():
    return 'World!'

@task
def task3(in1, in2):
    print(f'{in1} {in2}')


with DAG(
    dag_id='taskflow_demo',
    start_date=datetime(2021, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    task3(task1(), task2())
