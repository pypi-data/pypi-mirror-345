"""This module contains functions for running commands in parallel in a managed environment."""

import os
from typing import List, Optional

from dnv.onecompute.file_service import FileTransferOptions
from dnv.onecompute.flowmodel import ParallelWork, SchedulingOptions, WorkUnit

from ...oneworkflow.composite_executable_command import CompositeExecutableCommand
from ...oneworkflow.oneworkflowclient import OneWorkflowClient

# pylint: disable=W0611:unused-import
from ...oneworkflow.utils.workunit_extension import (
    transfer_files_from_loadcase_to_output_directory,
    with_shared_files_copied_to_loadcase,
)
from ._workflow_utils_private import _assign_default_if_none, _is_directory_empty
from .command_info import CommandInfo
from .workflow_runners_managed import run_managed_workflow_async


async def run_managed_commands_in_parallel_async(
    client: OneWorkflowClient,
    commands_info: List[CommandInfo],
    job_preparation_work: Optional[WorkUnit] = None,
    job_release_work: Optional[WorkUnit] = None,
    log_job: bool = False,
    scheduling_options: Optional[SchedulingOptions] = None,
    enable_common_files_copy_to_load_cases: bool = False,
    files_to_exclude_from_common_files_copy: Optional[List[str]] = None,
    files_to_upload_from_client_to_blob: Optional[FileTransferOptions] = None,
    files_to_move_post_workflow_execution: Optional[List[str]] = None,
    files_to_download_from_blob_to_client: Optional[FileTransferOptions] = None,
):
    """
    Executes a set of commands in parallel in a managed environment, handling both local and
    cloud runs.

    This function orchestrates the execution of a list of `CommandInfo` objects in a managed
    workflow. Each `CommandInfo` represents a set of commands to execute, wrapped in a
    `ParallelWork` structure for efficient parallel execution.

    In a managed environment, the function takes care of initiating and terminating the
    workflow runtime service for local runs, and handles login and authentication for cloud
    runs. It also manages the file upload and download of results and logs.

    Using the provided `OneWorkflowClient`, the function submits the commands for execution
    and retrieves necessary logs and results upon completion.

    Args:
        client (OneWorkflowClient): The client used to interact with the workflow system.
        commands_info (List[CommandInfo]): A list of commands to be executed.
        job_preparation_work (Optional[WorkUnit], optional): Work to be done in preparation for
            the job. Defaults to None.
        job_release_work (Optional[WorkUnit], optional): Work to be done after the job is
            completed. Defaults to None.
        log_job (bool, optional): Whether to log the job. Defaults to False.
        scheduling_options (Optional[SchedulingOptions], optional): Options for scheduling the
            job. Defaults to None.
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
        files_to_move_post_workflow_execution (Optional[List[str]]): An optional list of glob
            patterns identifying files to be moved from the load-case directory to the specified
            output directory (also known as a result folder) after workflow execution. This applies
            to both local and cloud executions. In local execution, files are moved within the temp
            job folder acting as the worker node. In cloud execution, files are moved within the
            worker node itself. This attribute allows for selective file transfer after the
            workflow. The files are moved when the load-case and output directories are not the
            same. If not specified, all files are moved.
        files_to_download_from_blob_to_client(Optional[FileTransferOptions], optional): An optional
            configuration defining the files to be downloaded from blob storage to the client
            machine. This configuration allows the specification of file size limits and file
            patterns to download.
            It defaults to FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]), which means
            files up to 10 MB and matching the wildcard **/*.* will be downloaded. This attribute
            facilitates selective file download from blob storage. If not specified, all files that
            match the default pattern and size limit will be downloaded.

    Returns:
            None: This function runs asynchronously and does not return a value.
    """
    files_to_exclude_from_common_files_copy = _assign_default_if_none(
        files_to_exclude_from_common_files_copy, ["**/*.py"]
    )

    files_to_upload_from_client_to_blob = _assign_default_if_none(
        files_to_upload_from_client_to_blob, FileTransferOptions()
    )

    files_to_move_post_workflow_execution = _assign_default_if_none(
        files_to_move_post_workflow_execution, ["**/*.*"]
    )

    files_to_download_from_blob_to_client = _assign_default_if_none(
        files_to_download_from_blob_to_client,
        FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]),
    )

    parallel_work = ParallelWork()

    for info in commands_info:
        # Define directories for load case
        load_case_foldername = info.load_case_foldername

        load_case_working_directory = os.path.join(
            client.load_cases_directory, load_case_foldername
        )

        load_case_results_directory = os.path.join(
            client.results_directory, load_case_foldername
        )

        download_files_from_blob = info.files_to_download_from_blob_to_worker_node
        upload_files_to_blob = info.files_to_upload_from_worker_node_to_blob

        # Create command and add to work unit
        command = CompositeExecutableCommand(info.commands, load_case_working_directory)
        work_unit = parallel_work.add(command, work_unit_id=info.load_case_foldername)

        # Define input and output directories for the work unit. These directories will be used
        # when creating the file transfer specification.
        assert client.workspace_info is not None
        folder_path = os.path.join(
            client.workspace_info.load_cases_fullpath, info.load_case_foldername
        )
        if not _is_directory_empty(folder_path):
            work_unit.input_directory(
                load_case_working_directory, include_files=download_files_from_blob
            )

        work_unit.output_directory(
            load_case_results_directory, include_files=upload_files_to_blob
        )

        # Copy common files to load case if required
        if enable_common_files_copy_to_load_cases and isinstance(work_unit, WorkUnit):
            # We are ignoring the type check and disabling the Pylint warning on this line because
            # the method 'with_shared_files_copied_to_loadcase' is added to 'work_unit'
            # through monkey patching, so static type checkers and linters may not recognize it.
            # pylint: disable=maybe-no-member
            work_unit.with_shared_files_copied_to_loadcase(  # type: ignore
                client.common_directory, files_to_exclude_from_common_files_copy
            )

        if (
            load_case_working_directory != load_case_results_directory
            and files_to_move_post_workflow_execution
        ):
            # We are ignoring the type check and disabling the Pylint warning on this line because
            # the method 'transfer_files_from_loadcase_to_output_directory' is added to 'work_unit'
            # through monkey patching, so static type checkers and linters may not recognize it.
            # pylint: disable=maybe-no-member
            work_unit = work_unit.transfer_files_from_loadcase_to_output_directory(  # type: ignore
                include_files=files_to_move_post_workflow_execution,
                load_case_folder=load_case_working_directory,
                results_folder=load_case_results_directory,
            )

    # Run workflow asynchronously
    await run_managed_workflow_async(
        client=client,
        work=parallel_work,
        job_preparation_work=job_preparation_work,
        job_release_work=job_release_work,
        log_job=log_job,
        scheduling_options=scheduling_options,
        enable_common_files_copy_to_load_cases=False,
        files_to_exclude_from_common_files_copy=files_to_exclude_from_common_files_copy,
        files_to_upload_from_client_to_blob=files_to_upload_from_client_to_blob,
        files_to_download_from_blob_to_client=files_to_download_from_blob_to_client,
    )
