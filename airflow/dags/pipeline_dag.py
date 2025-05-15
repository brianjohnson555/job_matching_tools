from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta


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
    },
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
    )

    if False:
        # Grouped parallel tasks
        with TaskGroup("scrapers") as task_scraper:
            for i, url in enumerate(SCRAPE_TARGETS):
                DockerOperator(
                    task_id=f"scraper_{i}",
                    image="docker_scraper:latest",
                    api_version='auto',
                    auto_remove='success',
                    command=(
                        "python lambda_func_scraper.py "
                        "'{{ params | tojson | replace('\"', '\\\"') }}'"
                    ),
                    docker_url="unix://var/run/docker.sock",
                    network_mode="bridge",
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

    task_dispatcher #>> task_scraper >> task_analyzer