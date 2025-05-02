"""
This module contains functions for running a single worker command or a sequence of them in a
managed environment.
"""

from typing import List, Optional, Union

from dnv.onecompute.file_service import FileTransferOptions
from dnv.onecompute.flowmodel import FileSelectionOptions, SchedulingOptions, WorkUnit

from ...oneworkflow.composite_executable_command import (
    CompositeExecutableCommand as SequentialExecutableCommand,
)
from ...oneworkflow.oneworkflowclient import OneWorkflowClient
from ...oneworkflow.worker_command import WorkerCommand
from ._workflow_utils_private import _assign_default_if_none
from .workflow_runners_managed import run_managed_workflow_async


async def run_managed_commands_in_sequence_async(
    client: OneWorkflowClient,
    worker_command: Union[WorkerCommand, List[WorkerCommand]],
    job_preparation_work: Optional[WorkUnit] = None,
    job_release_work: Optional[WorkUnit] = None,
    log_job: bool = False,
    scheduling_options: Optional[SchedulingOptions] = None,
    enable_common_files_copy_to_load_cases: bool = False,
    files_to_exclude_from_common_files_copy: Optional[List[str]] = None,
    input_directories_for_worker_command: Optional[List[FileSelectionOptions]] = None,
    output_directory_for_worker_command: Optional[FileSelectionOptions] = None,
    files_to_upload_from_client_to_blob: Optional[FileTransferOptions] = None,
    files_to_download_from_blob_to_client: Optional[FileTransferOptions] = None,
):
    """
    Executes a single worker command or a sequence of them in a managed environment, handling both
    local and cloud runs.

    In a managed environment, the function initiates and terminates the workflow runtime service for
    local runs, and handles login and authentication for cloud runs. It also manages the upload and
    download of result files and logs.

    Using the provided `OneWorkflowClient`, the function submits the worker commands for execution
    and retrieves necessary logs and results upon completion.

    Args:
        client (OneWorkflowClient): The instance of OneWorkflowClient for accessing the OneWorkflow
            service.
        worker_command (Union[WorkerCommand, List[WorkerCommand]]): The worker command or a list of
            worker commands to be executed.
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
        input_directories_for_worker_command  (Optional[List[FileSelectionOptions]]): A list of
            directories located in blob storage that contain necessary files for executing the
            worker command. Before the worker command is executed, these files are copied to the
            corresponding loadcase folder on a worker node. Each directory in this list should be a
            path to a folder in blob storage. If this is not specified, the worker command will
            determine the input directory based on the worker command's working directory.
        output_directory_for_worker_command (Optional[FileSelectionOptions]): Specifies the blob
            storage directory where the output files of the worker command will be stored. If not
            provided, the output files will be stored in the default results directory of the
            OneComputeClient.
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
            It defaults to FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]),which means
            files up to 10 MB and matching the wildcard **/*.* will be downloaded. This attribute
            facilitates selective file download from blob storage. If not specified, all files that
            match the default pattern and size limit will be downloaded.

    Returns:
            None: This function runs asynchronously and does not return a value.
    """
    files_to_upload_from_client_to_blob = _assign_default_if_none(
        files_to_upload_from_client_to_blob, FileTransferOptions()
    )
    files_to_download_from_blob_to_client = _assign_default_if_none(
        files_to_download_from_blob_to_client,
        FileTransferOptions(max_size="10 MB", patterns=["**/*.*"]),
    )

    working_dir = _get_working_dir(worker_command, input_directories_for_worker_command)
    if not working_dir:
        print("Error: Working directory is not specified.")
        return

    work_unit = _setup_work_unit(
        worker_command,
        working_dir,
        input_directories_for_worker_command,
        output_directory_for_worker_command,
        client.results_directory,
    )

    await run_managed_workflow_async(
        client=client,
        work=work_unit,
        job_preparation_work=job_preparation_work,
        job_release_work=job_release_work,
        log_job=log_job,
        scheduling_options=scheduling_options,
        enable_common_files_copy_to_load_cases=enable_common_files_copy_to_load_cases,
        files_to_exclude_from_common_files_copy=files_to_exclude_from_common_files_copy,
        files_to_upload_from_client_to_blob=files_to_upload_from_client_to_blob,
        files_to_download_from_blob_to_client=files_to_download_from_blob_to_client,
    )


def _get_working_dir(
    worker_command: Union[WorkerCommand, List[WorkerCommand]],
    input_directories_for_worker_command: Optional[List[FileSelectionOptions]],
) -> Optional[str]:
    """
    Determines the working directory for a worker command.

    Args:
        worker_command (Union[WorkerCommand, List[WorkerCommand]]): The worker command or a list of
            worker commands.
        input_directories_for_worker_command (Optional[List[FileSelectionOptions]]): A list of file
            selection options for input directories.

    Returns:
        Optional[str]: The working directory for the worker command. If no working directory is
        found, returns None.
    """
    working_dir: Optional[str] = None

    # If worker_command is a list, retrieve the working_directory from the first command
    # that has a defined (non-None) working_directory
    if isinstance(worker_command, list):
        working_dir = next(
            (cmd.working_directory for cmd in worker_command if cmd.working_directory),
            None,
        )
    else:
        working_dir = worker_command.working_directory

    # If working_dir is still not defined, try to get it from input_directories_for_worker_command
    if not working_dir and input_directories_for_worker_command:
        working_dir = input_directories_for_worker_command[0].directory

    return working_dir


def _setup_work_unit(
    worker_command: Union[WorkerCommand, List[WorkerCommand]],
    working_dir: str,
    input_directories_for_worker_command: Optional[List[FileSelectionOptions]],
    output_directory_for_worker_command: Optional[FileSelectionOptions],
    results_directory: str,
) -> WorkUnit:
    """
    Sets up a work unit with the given parameters.

    Args:
        worker_command (Union[WorkerCommand, List[WorkerCommand]]): The worker command or a list of
            worker commands.
        working_dir (str): The working directory.
        input_directories_for_worker_command (Optional[List[FileSelectionOptions]]): A list of file
            selection options for input directories.
        output_directory_for_worker_command (Optional[FileSelectionOptions]): File selection options
            for the output directory.
        results_directory (str): The results directory.

    Returns:
        WorkUnit: The setup work unit.
    """
    work_unit = (
        WorkUnit(SequentialExecutableCommand(worker_command, working_dir=working_dir))
        if isinstance(worker_command, list)
        else WorkUnit(worker_command)
    )
    work_unit = _setup_input_directory(
        work_unit, input_directories_for_worker_command, working_dir
    )
    work_unit = _setup_output_directory(
        work_unit, output_directory_for_worker_command, results_directory
    )
    return work_unit


def _setup_input_directory(
    work_unit: WorkUnit,
    input_directories_for_worker_command: Optional[List[FileSelectionOptions]],
    working_dir: str,
) -> WorkUnit:
    """
    Sets up the input directory for a work unit.

    Args:
        work_unit (WorkUnit): The work unit.
        input_directories_for_worker_command (Optional[List[FileSelectionOptions]]): A list of file
            selection options for input directories.
        working_dir (str): The working directory.

    Returns:
        WorkUnit: The work unit with the input directory set up.
    """
    if input_directories_for_worker_command:
        for source_dir in input_directories_for_worker_command:
            work_unit = work_unit.input_directory(
                directory=source_dir.directory,
                include_files=source_dir.include_files,
                exclude_files=source_dir.exclude_files,
            )
    elif working_dir:
        work_unit = work_unit.input_directory(directory=working_dir)
    return work_unit


def _setup_output_directory(
    work_unit: WorkUnit,
    output_directory_for_worker_command: Optional[FileSelectionOptions],
    results_directory: str,
) -> WorkUnit:
    """
    Sets up the output directory for a work unit.

    Args:
        work_unit (WorkUnit): The work unit.
        output_directory_for_worker_command (Optional[FileSelectionOptions]): File selection
            options for the output directory.
        results_directory (str): The results directory.

    Returns:
        WorkUnit: The work unit with the output directory set up.
    """
    if output_directory_for_worker_command:
        work_unit = work_unit.output_directory(
            directory=output_directory_for_worker_command.directory,
            include_files=output_directory_for_worker_command.include_files,
            exclude_files=output_directory_for_worker_command.exclude_files,
        )
    else:
        work_unit = work_unit.output_directory(directory=results_directory)
    return work_unit
