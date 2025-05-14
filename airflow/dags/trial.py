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
    schedule_interval='@daily',
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
) as dag:
    
    # Rank step after all scrapers finish
    task_dispatcher = DockerOperator(
        task_id="rank_jobs",
        image="docker_dispatcher:latest",
        api_version='auto',
        auto_remove=True,
        command="",  # Add args if needed
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    # Grouped parallel tasks
    with TaskGroup("scrapers") as task_scraper:
        for i, url in enumerate(SCRAPE_TARGETS):
            DockerOperator(
                task_id=f"scrape_{i}",
                image="docker-scraper:latest",
                api_version='auto',
                auto_remove=True,
                command=f"--url {url}",
                docker_url="unix://var/run/docker.sock",
                network_mode="bridge",
            )

    # Rank step after all scrapers finish
    task_rank = DockerOperator(
        task_id="rank_jobs",
        image="docker-analyzer:latest",
        api_version='auto',
        auto_remove=True,
        command="",  # Add args if needed
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    task_dispatcher >> task_scraper >> task_rank