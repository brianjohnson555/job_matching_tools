from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.models.xcom_arg import XComArg
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

def build_expand_input(ti):
    import json
    import logging

    try:
        result = ti.xcom_pull(task_ids="task_dispatcher", key="return_value")
        url_list = result["url_list"]
        query = result["query"]

        if isinstance(url_list, str):
            url_list = json.loads(url_list)  # Parse JSON string if needed

        return [{"URL": url, "QUERY": query} for url in url_list]

    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        raise  # Ensure Airflow marks task as failed


default_args = {
    'owner': 'you',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# URLs to scrape – parameterized inputs
SCRAPE_TARGETS = [f"https://example.com/jobs?page={i}" for i in range(1, 11)]

with DAG(
    dag_id='job_scraper_pipeline',
    default_args=default_args,
    description='Run scraper containers in parallel, then rank and publish',
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
    params={# default values
        "query": "Data Scientist",
        "location": "Chicago",
        "pages": 1,
        "post_time": 1,
        "word_scores": {
            "phd": 1.1,
            "python": 1.1,
            "senior": 0.8
            }
    }
) as dag:
    
    # Rank step after all scrapers finish
    task_dispatcher = DockerOperator(
        task_id="dispatcher",
        image="docker_dispatcher:latest",
        api_version='auto',
        auto_remove='success',
        command=(
            "python lambda_func_dispatcher.py "
            "'{{ params | tojson | replace('\"', '\\\"') }}'"
        ),
        docker_url="unix://var/run/docker.sock",
        tty=True,
        network_mode="bridge",
        do_xcom_push=True,
    )

    task_load_urls = PythonOperator(
        task_id="load_urls",
        python_callable=build_expand_input
    )

    task_scraper = DockerOperator.partial(
        task_id=f"scraper",
        image="docker_scraper:latest",
        api_version='auto',
        auto_remove='success',
        command=(
            "python lambda_func_scraper.py {{ params.item }}"
        ),
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    ).expand(
        environment=XComArg(task_load_urls)
    )

    # Rank step after all scrapers finish
    task_analyzer = DockerOperator(
        task_id="analyzer",
        image="docker_analyzer:latest",
        api_version='auto',
        auto_remove='success',
        command="",  # Add args if needed
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    task_dispatcher >> task_load_urls >> task_scraper >> task_analyzer