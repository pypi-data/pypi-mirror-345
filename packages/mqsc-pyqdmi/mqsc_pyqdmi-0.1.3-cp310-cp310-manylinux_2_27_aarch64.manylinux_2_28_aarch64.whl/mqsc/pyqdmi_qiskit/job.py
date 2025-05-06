# Copyright (c) 2025 Munich Quantum Software Company GmbH
# All rights reserved.
#
# This file is part of MQSC PyQDMI. Use of this file is subject to a commercial
# license. See LICENSE.txt for details.

"""MQSC PyQDMI Qiskit Job."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from qiskit.providers import JobStatus, JobV1
from qiskit.result import Result
from qiskit.result.models import ExperimentResult

from mqsc.pyqdmi import Job  # type: ignore[import-not-found]
from mqsc.pyqdmi import JobStatus as QDMIJobStatus

if TYPE_CHECKING:
    from .backend import QiskitBackend


__all__ = ["QiskitJob"]


def __dir__() -> list[str]:
    return __all__


class QiskitJob(JobV1):  # type: ignore[misc]
    """Implementation of Qiskit's job interface to handle circuit execution."""

    def __init__(self, backend: QiskitBackend, job: Job, name: str) -> None:
        """Initialize the job.

        Args:
            backend: The backend to use for the job.
            job: The job object from QDMI.
            name: The name of the circuit the job is associated with.
        """
        super().__init__(backend=backend, job_id=job.id)
        self._job = job
        self._counts: dict[str, int] | None = None
        self._name = name

    def result(self) -> Result:
        """Get the result of the job.

        Returns:
            The result of the job.
        """
        if self._counts is None:
            self._job.wait()
            self._counts = self._job.get_counts()
        return Result(
            backend_name=None,
            backend_version=None,
            qobj_id=None,
            job_id=self.job_id(),
            success=True,
            date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            results=[
                ExperimentResult.from_dict({
                    "success": True,
                    "shots": self._job.num_shots,
                    "data": {"counts": self._counts, "metadata": {}},
                    "header": {"name": self._name},
                })
            ],
        )

    def status(self) -> JobStatus:
        """Get the status of the job.

        Returns:
            The status of the job.

        Raises:
            ValueError: If the job status is unknown.
        """
        status = self._job.status()
        if status == QDMIJobStatus.DONE:
            return JobStatus.DONE
        if status == QDMIJobStatus.RUNNING:
            return JobStatus.RUNNING
        if status == QDMIJobStatus.CANCELED:
            return JobStatus.CANCELLED
        if status == QDMIJobStatus.SUBMITTED:
            return JobStatus.QUEUED
        if status == QDMIJobStatus.CREATED:
            return JobStatus.INITIALIZING
        msg = f"Unknown job status: {status}"
        raise ValueError(msg)

    def submit(self) -> None:
        """Submit the job."""
        msg = (
            "You should never have to submit jobs by calling this method. "
            "The job instance is only for checking the progress and retrieving the results of the submitted job."
        )
        raise NotImplementedError(msg)
