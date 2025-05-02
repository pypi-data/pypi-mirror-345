"""This module defines the JobResult class, which encapsulates the results of a job execution."""

from typing import List

from dnv.onecompute import JobInfo, WorkItemInfo


class JobResult:
    """
    Represents the result of a job, including its status and associated work items.

    Attributes:
        job_info (JobInfo): Contains information about the job's status.
        work_items_info (List[WorkItemInfo]): A list of WorkItemInfo objects, each containing
            information about the status of a work item associated with the job.
    """

    def __init__(self, job_info: JobInfo, work_items_info: List[WorkItemInfo]):
        self.job_info: JobInfo = job_info
        self.work_items_info: List[WorkItemInfo] = work_items_info
