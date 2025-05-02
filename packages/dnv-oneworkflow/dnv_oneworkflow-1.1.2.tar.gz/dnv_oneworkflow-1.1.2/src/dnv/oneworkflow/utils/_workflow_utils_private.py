""" This module contains private utility functions for the OneWorkflowClient class. """

import asyncio
import os

from dnv.onecompute import JobEventArgs, OneComputeClient, WorkItemEventArgs, WorkStatus
from dnv.onecompute.file_service import FileTransferOptions
from dnv.onecompute.flowmodel import WorkUnit

from ...oneworkflow.oneworkflowclient import OneWorkflowClient
from .platform import Platform

# A string representing the local application identifier.
LOCAL_APP_ID = "OneWorkflowWorkerHost"

# A string representing the cloud application identifier, which is the same as the local app ID
# in this case.
CLOUD_APP_ID = LOCAL_APP_ID


def _worker_host_executable_name(cloud_run: bool) -> str:
    """
    Gets the name of the worker host executable based on the execution context.

    Args:
        cloud_run (bool): A boolean indicating whether the code is running in a cloud context.

    Returns:
        str: The name of the executable. If cloud_run is False, an empty string is returned.
        Otherwise, it returns "OneWorkflowWorkerHost".
    """
    return "" if not cloud_run else CLOUD_APP_ID


def _oc_application_id(cloud_run: bool, platform: Platform) -> str:
    """
    Gets the application ID based on the execution context and platform.

    Args:
        cloud_run (bool): A boolean indicating whether the code is running in a cloud context.
            platform (Platform): An enum representing the platform.

    Returns:
        str: The application ID based on the input parameters. If cloud_run is True, it returns
        "OneWorkflowWorkerLinux" for Linux or "OneWorkflowWorkerWindows" for Windows. If
        cloud_run is False, it returns the local application ID (LOCAL_APP_ID).
    """
    return (
        (
            "OneWorkflowWorkerLinux"
            if platform == Platform.LINUX
            else "OneWorkflowWorkerWindows"
        )
        if cloud_run
        else LOCAL_APP_ID
    )


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Get or create an asyncio event loop.

    Returns:
        asyncio.AbstractEventLoop: An asyncio event loop.
    """
    loop: asyncio.AbstractEventLoop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        print("Info: No event loop is running. Creating a new one.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
    return loop


def _is_directory_empty(folder_path: str):
    """
    Checks if a directory and its subdirectories are empty.

    This function uses os.walk to traverse through a directory and its subdirectories. If any
    files are found, it returns False, indicating that the directory is not empty. If no files
    are found after traversing the entire directory tree, it returns True, indicating that the
    directory is empty.

    Parameters:
        folder_path (str): The path of the directory to check.

    Returns:
        bool: False if the directory or any of its subdirectories contain files, True otherwise.
    """
    for _, _, files in os.walk(folder_path):
        if files:
            return False
    return True


def _assign_default_if_none(variable, default_value):
    """Assigns default value to variable if variable is None"""
    return variable if variable is not None else default_value


def _work_item_status_changed_callback(
    client: OneWorkflowClient, option: FileTransferOptions
):
    """
    Create a 'work_item_status_changed' callback function.

    This function returns a callback that can be used when registering a 'work_item_status_changed'
    event handler. The callback will handle changes in the status of work items, printing status
    information and performing actions such as downloading job logs and result files based on the
    work item's status.

    Args:
        client (OneWorkflowClient): An instance of the OneWorkflowClient for interacting with
            the OneWorkflow system.
        option (FileTransferOptions): An option specifying how to handle files during the callback's
            execution.

    Returns:
        callable: A 'work_item_status_changed' callback function suitable for event registration.
    """

    async def work_item_status_changed(_: OneComputeClient, event: WorkItemEventArgs):
        print(
            f"Info: The status of work item '{event.work_item_id}' is '{event.work_status.name}'"
        )
        if event.work_status in [
            WorkStatus.Completed,
            WorkStatus.Faulted,
            WorkStatus.Aborted,
        ]:
            # Download logs for the job and work item
            client.download_job_logs(event.job_id, event.work_item_id)

            # Download result files for the job and work item
            if event.work_status != WorkStatus.Aborted:
                await client.download_result_files_async(
                    event.job_id, event.work_item_id, option
                )

    return work_item_status_changed


def _workflow_completion_trigger(
    client: OneWorkflowClient, option: FileTransferOptions, work_unit: WorkUnit
):
    """
    Create a 'work_item_status_changed' callback function for kicking off the next workflow in a
    workflow pipeline.

    This function returns a callback that can be used when registering a 'work_item_status_changed'
    event handler. The callback monitors the status of work items and, when a work item completes
    successfully, triggers the execution of the next workflow in the workflow pipeline defined by
    the provided `work_unit`.

    Args:
        client (OneWorkflowClient): An instance of the OneWorkflowClient for interacting with
            the OneWorkflow system.
        option (FileTransferOptions): An option specifying how to handle files during the callback's
            execution.
        work_unit (WorkUnit): The definition of the next job to be executed when a work item
            completes.

    Returns:
        callable: A 'work_item_status_changed' callback function suitable for event registration.
    """

    async def work_item_status_changed(_: OneComputeClient, event: WorkItemEventArgs):
        print(
            f"Info: The status of work item '{event.work_item_id}' is '{event.work_status.name}'"
        )
        if event.work_status in [
            WorkStatus.Completed,
        ]:
            await client.run_workflow_async(
                work_unit,
                work_item_status_changed=_work_item_status_changed_callback(
                    client, option
                ),
                log_job=True,
            )

    return work_item_status_changed


async def _job_status_changed(_: OneComputeClient, event: JobEventArgs):
    """
    Asynchronous function that is triggered when a job's status changes.
    It prints the job's ID, status, progress percentage, and message.

    Args:
        _ (OneComputeClient): The OneComputeClient instance. This argument is not used in the
            function and is therefore named '_'.
        event (JobEventArgs): The event arguments containing details about the job.
    """
    print(
        f"Info: "
        f"Job ID: {event.job_id}. "
        f"Job Status: {event.work_status.name}. "
        f"Job Progress: {int(event.progress * 100)}%. "
        f"Job Message: {event.message}"
    )


async def _job_progress_changed(_: OneComputeClient, event: JobEventArgs):
    """
    Handle the 'job progress changed' notification.

    This asynchronous function is designed to be used as a callback for the 'job_progress_changed'
    event. It prints information about the progress of a job, including the progress percentage and
    any associated message.

    Args:
        _: Placeholder for the OneComputeClient instance (not used in the function).
        event (JobEventArgs): An event object containing information about the job progress.
    """
    print(
        f"Info: The progress of the job is '{int(event.progress * 100)}%'. "
        f"The message is '{event.message}'"
    )


async def _work_item_progress_changed(_: OneComputeClient, event: WorkItemEventArgs):
    """
    Handle the 'work item progress changed' notification.

    This asynchronous function is designed to be used as a callback for the
    'work_item_progress_changed' event. It prints information about the progress of a work item,
    including the work item's ID and any associated message.

    Args:
        _: Placeholder for the OneComputeClient instance (not used in the function).
        event (WorkItemEventArgs): An event object containing information about the work item's
            progress.
    """
    print(f"Info: The work item {event.work_item_id} message is '{event.message}'")
