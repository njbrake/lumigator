from http import HTTPStatus

from schemas.deployments import DeploymentEvent

from mzai.backend.schemas.jobs import JobSubmissionResponse
from sdk.core import ApiClient
from sdk.healthcheck import HealthCheck


class Health:
    HEALTH_ROUTE = "health"

    def __init__(self, c: ApiClient):
        self.client = c

    def healthcheck(self) -> HealthCheck:
        """Returns healthcheck information."""
        check = HealthCheck()
        response = self.client.get_response(self.HEALTH_ROUTE)
        if response:
            data = response.json()
        check.status = data.get("status")
        check.deployment_type = data.get("deployment_type")

        return check

    def get_deployments(self) -> list[DeploymentEvent]:
        response = self.client.get_response(f"{self.HEALTH_ROUTE}/deployments")

        if not response:
            return []

        return [DeploymentEvent(**args) for args in response.json()]

    def get_jobs(self) -> list[JobSubmissionResponse]:
        """Returns information on all job submissions."""
        endpoint = f"{self.HEALTH_ROUTE}/jobs/"
        response = self.client.get_response(endpoint)

        if not response:
            return []

        return [JobSubmissionResponse(**job) for job in response.json()]


    def get_job(self, job_id: str) -> JobSubmissionResponse | None:
        """Returns information on the job submission for the specified ID."""
        endpoint = f"{self.HEALTH_ROUTE}/jobs/{job_id}"
        response = self.client.get_response(endpoint)

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return JobSubmissionResponse(**data)