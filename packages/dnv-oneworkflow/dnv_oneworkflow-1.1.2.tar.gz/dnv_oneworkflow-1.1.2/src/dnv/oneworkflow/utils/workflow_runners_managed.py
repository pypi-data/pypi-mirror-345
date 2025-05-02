"""
This module provides managed interfaces for executing workflows and file operations, including 
starting and stopping services, and uploading and downloading files, in both synchronous and 
asynchronous manners.
"""

from typing import Optional, Union

from dnv.onecompute.file_service import FileTransferOptions
from dnv.onecompute.flowmodel import ParallelWork, SchedulingOptions, WorkItem, WorkUnit

from ...oneworkflow.oneworkflowclient import OneWorkflowClient

# pylint: disable=W0611:unused-import
from ...oneworkflow.utils.workunit_extension import (
    transfer_files_from_loadcase_to_output_directory,
    with_shared_files_copied_to_loadcase,
)
from ._workflow_utils_private import (
    _assign_default_if_none,
    _get_or_create_event_loop,
    _job_progress_changed,
    _job_status_changed,
    _work_item_progress_changed,
    _work_item_status_changed_callback,
)
from .job_result import JobResult


def run_managed_workflow(
    client: OneWorkflowClient,
    work: Union[ParallelWork, WorkUnit, WorkItem],
    job_preparation_work: Optional[WorkUnit] = None,
    job_release_work: Optional[WorkUnit] = None,
    log_job: bool = False,
    scheduling_options: Optional[SchedulingOptions] = None,
    enable_common_files_copy_to_load_cases: bool = False,
    files_to_exclude_from_common_files_copy: Optional[list[str]] = None,
    files_to_upload_from_client_to_blob: Optional[FileTransferOptions] = None,
    files_to_download_from_blob_to_client: Optional[FileTransferOptions] = None,
) -> Optional[JobResult]:
    """
    This API manages the execution of workflows and file operations synchronously, with distinct
    behaviors for local and cloud runs.

    For local runs, the API initiates the workflow runtime service, executes the specified workflow
    using the provided OneWorkflowClient instance, and downloads the necessary logs and results.
    Once the operation is complete, it terminates the workflow runtime service.

    For cloud runs, the API handles user authentication through login, executes the specified
    workflow with the provided OneWorkflowClient instance, and downloads the necessary logs
    and results.

    Args:
        client (OneWorkflowClient): The instance of OneWorkflowClient for accessing the OneWorkflow
            service.
        work (Union[ParallelWork, WorkUnit, WorkItem]): The main work to be processed in the
            workflow.
        job_preparation_work (Optional[WorkUnit]): Additional work to be performed before the main
            job starts.
        job_release_work (Optional[WorkUnit]): Additional work to be performed after the main job
            finishes.
        log_job (bool): A boolean indicating whether the job is to be logged.
        scheduling_options (Optional[SchedulingOptions]): Options for job scheduling.
        enable_common_files_copy_to_load_cases (bool): A flag that, when set to True, enables the
            operation of copying files from the folder designated as a 'common-files' folder to each
            load case folder. This operation is applicable both locally and in the cloud. In a local
            execution context, files are copied from a temporary job folder(acting as a worker node)
            that contains the 'common-files' folder, to the load case folders under the job folder.
            In a cloud execution context, this operation happens on a worker node, copying from the
            'common-files' folder to the load case folders. Defaults to False.
        files_to_exclude_from_common_files_copy (List[str]): A list of file patterns to exclude
            during the operation of copying files from the folder designated as a 'common-files'
            folder to each load case folder. This exclusion applies both in local and cloud
            execution contexts. For instance, in a local execution context, when files are copied
            from a temporary job folder (acting as a worker node) that contains the 'common-files'
            folder, to the load case folders under the job folder, any files matching the patterns
            in this list will be excluded. Similarly, in a cloud execution context, when this
            operation happens on a worker node, copying from the 'common-files' folder to the load
            case folders, files matching these patterns will be excluded. This is useful for
            preventing certain types of files, such as Python files, from being copied to the load
            case folders. Defaults to ["**/*.py"] if not specified.
        files_to_upload_from_client_to_blob (Optional[FileTransferOptions], optional): An option for
            uploading files from the workspace folder on the client machine to blob storage. For
            local execution, files are copied from the workspace on the client machine to a
            temporary blob storage location. For cloud execution, files are uploaded directly
            from the client machine's workspace to cloud blob storage. This attribute facilitates
            selective file upload to blob storage before command execution. If not specified, it
            defaults to FileTransferOptions(), which means all files from the workspace will be
            uploaded.
        files_to_download_from_blob_to_client(Optional[FileTransferOptions], optional): An optional
            configuration defining the files to be downloaded from blob storage to the client
            machine. This configuration allows the specification of file size limits and file
            patterns to download.
            It defaults to FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]), which means
            files up to 10 MB and matching the wildcard **/*.* will be downloaded. This attribute
            facilitates selective file download from blob storage. If not specified,all files that
            match the default pattern and size limit will be downloaded.

    Returns:
        Optional[JobResult]: The result of the workflow, if it completed successfully. Returns None
        if the workflow did not yield a result or encountered a failure.
    """
    files_to_upload_from_client_to_blob = _assign_default_if_none(
        files_to_upload_from_client_to_blob, FileTransferOptions()
    )
    files_to_download_from_blob_to_client = _assign_default_if_none(
        files_to_download_from_blob_to_client,
        FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]),
    )

    event_loop = _get_or_create_event_loop()
    if event_loop:
        coroutine = run_managed_workflow_async(
            client=client,
            work=work,
            job_preparation_work=job_preparation_work,
            job_release_work=job_release_work,
            log_job=log_job,
            scheduling_options=scheduling_options,
            enable_common_files_copy_to_load_cases=enable_common_files_copy_to_load_cases,
            files_to_exclude_from_common_files_copy=files_to_exclude_from_common_files_copy,
            files_to_upload_from_client_to_blob=files_to_upload_from_client_to_blob,
            files_to_download_from_blob_to_client=files_to_download_from_blob_to_client,
        )
        try:
            return event_loop.run_until_complete(coroutine)
        except Exception as ex:
            print(ex)


async def run_managed_workflow_async(
    client: OneWorkflowClient,
    work: Union[ParallelWork, WorkUnit, WorkItem],
    job_preparation_work: Optional[WorkUnit] = None,
    job_release_work: Optional[WorkUnit] = None,
    log_job: bool = False,
    scheduling_options: Optional[SchedulingOptions] = None,
    enable_common_files_copy_to_load_cases: bool = False,
    files_to_exclude_from_common_files_copy: Optional[list[str]] = None,
    files_to_upload_from_client_to_blob: Optional[FileTransferOptions] = None,
    files_to_download_from_blob_to_client: Optional[FileTransferOptions] = None,
) -> Optional[JobResult]:
    """
    Manages the execution of workflows and file operations asynchronously, handling both local
    and cloud runs.

    The API handles both local and cloud runs. It uses the provided OneWorkflowClient instance to
    execute the specified workflow and manage the download of necessary logs and results.

    For local runs, the API initiates and terminates the workflow runtime service. For cloud
    runs, it handles user authentication through login. Once workflows complete, the necessary
    logs and results are downloaded.

    The function also allows for additional work to be performed before and after the main job,
    as well as the configuration of job scheduling options.

    Args:
        client (OneWorkflowClient): The instance of OneWorkflowClient for accessing the OneWorkflow
            service.
        work (Union[ParallelWork, WorkUnit, WorkItem]): The main work to be processed in the
            workflow.
        job_preparation_work (Optional[WorkUnit]): Additional work to be performed before the main
            job starts.
        job_release_work (Optional[WorkUnit]): Additional work to be performed after the main job
            finishes.
        log_job (bool): A boolean indicating whether the job is to be logged.
        scheduling_options (Optional[SchedulingOptions]): Options for job scheduling.
        enable_common_files_copy_to_load_cases (bool): A flag that, when set to True, enables the
            operation of copying files from the folder designated as a 'common-files' folder to each
            load case folder. This operation is applicable both locally and in the cloud. In a local
            execution context, files are copied from a temporary job folder(acting as a worker node)
            that contains the 'common-files' folder, to the load case folders under the job folder.
            In a cloud execution context, this operation happens on a worker node, copying from the
            'common-files' folder to the load case folders. Defaults to False.
        files_to_exclude_from_common_files_copy (List[str]): A list of file patterns to exclude
            during the operation of copying files from the folder designated as a 'common-files'
            folder to each load case folder. This exclusion applies both in local and cloud
            execution contexts. For instance, in a local execution context, when files are copied
            from a temporary job folder (acting as a worker node) that contains the 'common-files'
            folder, to the load case folders under the job folder, any files matching the patterns
            in this list will be excluded. Similarly, in a cloud execution context, when this
            operation happens on a worker node, copying from the 'common-files' folder to the load
            case folders, files matching these patterns will be excluded. This is useful for
            preventing certain types of files, such as Python files, from being copied to the load
            case folders. Defaults to ["**/*.py"] if not specified.
        files_to_upload_from_client_to_blob (Optional[FileTransferOptions], optional): An option for
            uploading files from the workspace folder on the client machine to blob storage. For
            local execution, files are copied from the workspace on the client machine to a
            temporary blob storage location. For cloud execution, files are uploaded directly
            from the client machine's workspace to cloud blob storage. This attribute facilitates
            selective file upload to blob storage before command execution. If not specified, it
            defaults to FileTransferOptions(), which means all files from the workspace will be
            uploaded.
        files_to_download_from_blob_to_client(Optional[FileTransferOptions], optional): An optional
            configuration defining the files to be downloaded from blob storage to the client
            machine. This configuration allows the specification of file size limits and file
            patterns to download.
            It defaults to FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]), which means
            files up to 10 MB and matching the wildcard **/*.* will be downloaded. This attribute
            facilitates selective file download from blob storage. If not specified,all files that
            match the default pattern and size limit will be downloaded.

    Returns:
        Optional[JobResult]: The result of the workflow, if it completed successfully. Returns None
        if the workflow did not yield a result or encountered a failure.
    """
    files_to_exclude_from_common_files_copy = _assign_default_if_none(
        files_to_exclude_from_common_files_copy, ["**/*.py"]
    )
    files_to_upload_from_client_to_blob = _assign_default_if_none(
        files_to_upload_from_client_to_blob, FileTransferOptions()
    )
    files_to_download_from_blob_to_client = _assign_default_if_none(
        files_to_download_from_blob_to_client,
        FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]),
    )

    job_result = None
    try:
        if client.cloud_run:
            client.login()

        client.start_workflow_runtime_service()
        client.upload_files(file_options=files_to_upload_from_client_to_blob)

        if enable_common_files_copy_to_load_cases and isinstance(work, WorkUnit):
            # We are ignoring the type check and disabling the Pylint warning on this line because
            # the method 'transfer_files_from_loadcase_to_output_directory' is added to 'work_unit'
            # through monkey patching, so static type checkers and linters may not recognize it.
            # pylint: disable=maybe-no-member
            work = work.with_shared_files_copied_to_loadcase(  # type: ignore
                client.common_directory, files_to_exclude_from_common_files_copy
            )

        work_item_status_changed_cb = _work_item_status_changed_callback(
            client, files_to_download_from_blob_to_client or FileTransferOptions()
        )

        job_id = await client.run_workflow_async(
            work=work,
            job_preparation_work=job_preparation_work,
            job_release_work=job_release_work,
            log_job=log_job,
            scheduling_options=scheduling_options,
            job_status_changed=_job_status_changed,
            job_progress_changed=_job_progress_changed,
            work_item_status_changed=work_item_status_changed_cb,
            work_item_progress_changed=_work_item_progress_changed,
        )

        if job_id and client.onecompute_client:
            job_info = client.onecompute_client.get_job_status(job_id)
            work_items_info = await client.onecompute_client.get_workitems_info_async(
                job_id
            )
            if job_info and work_items_info:
                job_result = JobResult(job_info, work_items_info)
    except Exception as ex:
        print(f"Error: An exception occurred while executing the workflow: {ex}")
    finally:
        client.stop_workflow_runtime_service()
    return job_result
