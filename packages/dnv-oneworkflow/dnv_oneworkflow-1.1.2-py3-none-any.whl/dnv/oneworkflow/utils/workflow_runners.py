"""This module contains functions for running a workflow job."""

from dnv.onecompute import Job
from dnv.onecompute.file_service import FileTransferOptions
from dnv.onecompute.flowmodel import WorkUnit

from ...oneworkflow.oneworkflowclient import OneWorkflowClient
from ._workflow_utils_private import (
    _job_progress_changed,
    _job_status_changed,
    _work_item_progress_changed,
    _work_item_status_changed_callback,
    _workflow_completion_trigger,
)


async def run_workflow_async(
    job: Job,
    client: OneWorkflowClient,
    option: FileTransferOptions = FileTransferOptions(
        max_size="12 MB", patterns=["**/*.txt", "**/*.lis", "**/*.mlg"]
    ),
):
    """
    Asynchronously runs a workflow job.

    This function is used to initiate the execution of a workflow job using the provided
    `job` and the OneWorkflowClient instance `client`. It allows you to specify optional
    file handling options through the `option` parameter.

    Args:
        job (Job): The job definition to be executed as part of the workflow.
        client (OneWorkflowClient): An instance of the OneWorkflowClient for interacting with
            the OneWorkflow system.
        option (FileTransferOptions, optional): Optional file handling options for the job's execution.
            Default options include a maximum file size of "12 MB" and patterns for file inclusion.
    """
    try:
        job_monitor = await client.submit_job_async(job)
        if not job_monitor:
            return

        jsc = job_monitor.job_status_changed
        jsc += _job_status_changed

        jpc = job_monitor.job_progress_changed
        jpc += _job_progress_changed

        wisc = job_monitor.work_item_status_changed
        wisc += _work_item_status_changed_callback(client, option)

        wipc = job_monitor.work_item_progress_changed
        wipc += _work_item_progress_changed

        await job_monitor.await_job_termination_async()
    except Exception as ex:
        print(ex)


async def run_workflow_async_two_clients(
    job: Job,
    client_linux: OneWorkflowClient,
    client_window: OneWorkflowClient,
    work_unit: WorkUnit,
    option: FileTransferOptions = FileTransferOptions(
        max_size="12 MB", patterns=["**/*.txt", "**/*.lis", "**/*.mlg"]
    ),
):
    """
    Asynchronously runs a workflow job with two different OneWorkflowClient instances.

    This function is used to initiate the execution of a workflow job using the provided
    `job` with two different OneWorkflowClient instances: `client_linux` for Linux platform
    and `client_window` for Windows platform. It also allows you to specify a `work_unit` and
    optional file handling options through the `option` parameter.

    Args:
        job (Job): The job definition to be executed as part of the workflow.
        client_linux (OneWorkflowClient): An instance of the OneWorkflowClient for Linux
            platform.
        client_window (OneWorkflowClient): An instance of the OneWorkflowClient for Windows
            platform.
        work_unit (WorkUnit): The definition of the next job to be executed in the workflow.
        option (FileTransferOptions, optional): Optional file handling options for the job's
            execution. Default options include a maximum file size of "12 MB" and patterns for
            file inclusion.
    """
    try:
        job_monitor = await client_linux.submit_job_async(job)
        if not job_monitor:
            return

        print("Info: Starting job with job-id:" + str(job.JobId))

        jsc = job_monitor.job_status_changed
        jsc += _job_status_changed

        jpc = job_monitor.job_progress_changed
        jpc += _job_progress_changed

        wisc = job_monitor.work_item_status_changed
        wisc += _workflow_completion_trigger(client_window, option, work_unit)

        wipc = job_monitor.work_item_progress_changed
        wipc += _work_item_progress_changed

        await job_monitor.await_job_termination_async()
    except Exception as ex:
        print(ex)
