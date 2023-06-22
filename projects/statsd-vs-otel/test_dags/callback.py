from airflow import DAG
from airflow.decorators import task
from airflow.utils.timezone import datetime
from airflow.utils.trigger_rule import TriggerRule


@task
def task_fails():
    assert False


@task(trigger_rule=TriggerRule.ALL_DONE)
def task_succeeds():
    assert True


def success_callback(context):
    print(f"DAG has succeeded, run_id: {context['run_id']}")


def failure_callback(context):
    print(f"Task has failed, task_instance_key_str: {context['task_instance_key_str']}")


with DAG(
    dag_id='callbacks',
    start_date=datetime(2021, 1, 1),
    schedule=None,
    catchup=False,
    on_success_callback=success_callback,
    on_failure_callback=failure_callback,
) as dag:

    task_fails() >> task_succeeds()


