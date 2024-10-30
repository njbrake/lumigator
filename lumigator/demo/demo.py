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
    logger.info("Starting demo")
    datasets = lumi_client.datasets.get_datasets()
    if datasets.total > 0:
        for remove_ds in datasets.items:
            logger.info(f"Removing dataset {remove_ds.id}")
            lumi_client.datasets.delete_dataset(remove_ds.id)
    datasets = lumi_client.datasets.get_datasets()
    assert datasets.total == 0
    dataset = lumi_client.datasets.create_dataset(dataset=file, format=DatasetFormat.JOB)
    datasets = lumi_client.datasets.get_datasets()
    assert datasets.total == 1
    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    logger.info(lumi_client.datasets.get_dataset(dataset.id))
    # job_create = JobCreate(name="test-job-int-001", model="hf://distilbert/distilbert-base-uncased", dataset=dataset.id)
    job_create = JobCreate(name="test-job-int-001", model="hf://distilgpt2", dataset=dataset.id)
    job_create.description = "This is a test job"
    job_create.max_samples = 2
    job_ret = lumi_client.jobs.create_job(JobType.EVALUATION, job_create)
    assert job_ret is not None
    jobs = lumi_client.jobs.get_jobs()
    assert jobs is not None
    assert len(jobs.items) == jobs.total

    job_status = asyncio.run(lumi_client.jobs.wait_for_job(job_ret.id))
    logger.info(job_status)

    link_info = lumi_client.jobs.get_dataset_link(job_ret.id)
    logger.info(f'List of downloadable URLs: {link_info.download_urls}')
    results = requests.get(link_info.download_urls[0], allow_redirects=True)
    open('result.dataset', 'wb').write(results.content)