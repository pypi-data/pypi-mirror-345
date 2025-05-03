from enum import Enum
from typing import Union, Dict, Any

from pythonik.models.base import Response
from pythonik.models.jobs.job_body import JobBody
from pythonik.models.jobs.job_response import JobResponse
from pythonik.specs.base import Spec


CREATE_JOB_PATH = "jobs/"
UPDATE_JOB_PATH = "jobs/{}"


class JobSpec(Spec):
    server = "API/jobs/"

    def create(
        self,
        body: Union[JobBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs
    ) -> Response:
        """
        Create a job

        Args:
            body: Job creation parameters, either as JobBody model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response[JobResponse]
        """
        json_data = self._prepare_model_data(body, exclude_defaults=exclude_defaults)
        resp = self._post(
            CREATE_JOB_PATH,
            json=json_data,
            **kwargs
        )

        return self.parse_response(resp, JobResponse)

    def update(
        self,
        job_id: str,
        body: Union[JobBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs
    ) -> Response:
        """
        Update a job

        Args:
            job_id: The ID of the job to update
            body: Job update parameters, either as JobBody model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response[JobResponse]
        """
        json_data = self._prepare_model_data(body, exclude_defaults=exclude_defaults)
        resp = self._patch(
            UPDATE_JOB_PATH.format(job_id),
            json=json_data,
            **kwargs
        )

        return self.parse_response(resp, JobResponse)
