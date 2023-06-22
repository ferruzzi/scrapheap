import time
from datetime import timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.utils.timezone import datetime


def sla_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    print(
        "The callback arguments are: ",
        {
            "dag": dag,
            "task_list": task_list,
            "blocking_task_list": blocking_task_list,
            "slas": slas,
            "blocking_tis": blocking_tis,
        },
    )


@task(sla=timedelta(seconds=10))
def sleep_20():
    """Sleep for 20 seconds"""
    time.sleep(20)


@task
def sleep_30():
    """Sleep for 30 seconds"""
    time.sleep(30)


with DAG(
    dag_id='fail_S_L_A',
    start_date=datetime(2021, 1, 1),
    schedule="*/2 * * * *",
    catchup=False,
    sla_miss_callback=sla_callback,
) as dag:

    sleep_20() >> sleep_30()
