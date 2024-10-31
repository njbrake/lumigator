import asyncio
from pathlib import Path
from time import sleep

import requests

from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.jobs import JobCreate, JobStatus, JobType

from lumigator_sdk.lumigator import LumigatorClient
from loguru import logger

lumi_client = LumigatorClient("localhost:8000")
dialog_data = "dialogsum_exc.csv"

with Path.open(dialog_data) as file:
    logger.info("Dataset handling")
    datasets = lumi_client.datasets.get_datasets()
    logger.info(f'Current datasets: \n{datasets}')
    dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.JOB)
    dataset_id = lumi_client.datasets.get_dataset(dataset.id)
    logger.info(f'Uploading dataset{dataset_id}')

    logger.info("Job creation")
    job_create = JobCreate(name="test-job-int-001", model="hf://distilgpt2", dataset=dataset.id)
    job_create.description = "This is a test job"
    job_create.max_samples = 2
    job_ret = lumi_client.jobs.create_job(JobType.EVALUATION, job_create)
    logger.info(f'Created job: {job_ret.id}')
    jobs = lumi_client.jobs.get_jobs()
    logger.info(f'Current jobs: \n{jobs}')
    logger.info("Waiting for job to end...")
    job_status = asyncio.run(lumi_client.jobs.wait_for_job(job_ret.id))

    logger.info("Job results")
    download_info = lumi_client.jobs.get_job_download(job_ret.id)
    logger.info(f'Getting result from {download_info.download_url}')
    results = requests.get(download_info.download_url, allow_redirects=True)
    logger.info(f'Result preview: {results.content[:80]}...')
    