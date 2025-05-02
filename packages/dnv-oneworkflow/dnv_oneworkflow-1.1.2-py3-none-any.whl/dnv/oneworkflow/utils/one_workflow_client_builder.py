"""This module provides a function to construct and configure instances of OneWorkflowClient."""

import platform as os_platform
from typing import Optional

from dnv.onecompute import AutoDeployOption, Environment
from dnv.onecompute.enums import LogLevel

from ...oneworkflow.oneworkflowclient import OneWorkflowClient
from ._file_transfer_progress_indicator import FileTransferProgressIndicator
from ._workflow_utils_private import _oc_application_id, _worker_host_executable_name
from .platform import Platform
from .process_manager import ProcessManager


def one_workflow_client(
    cloud_run: bool,
    workspace_id: str,
    workspace_path: str,
    workspace_common_folder_name: str = "CommonFiles",
    workspace_load_cases_folder_name: str = "LoadCases",
    workspace_results_folder_name: str = "LoadCases",
    local_workflow_runtime_temp_folder_path: str = r"C:\Temp\OneWorkflow",
    local_workflow_runtime_path: Optional[str] = "",
    local_workflow_runtime_service_visible: bool = False,
    local_workflow_runtime_temp_folders_cleanup: bool = True,
    platform: Platform = Platform.WINDOWS,
    max_cores: Optional[int] = None,
    debug_local_worker: bool = False,
    local_worker_host_apps_path: Optional[str] = "",
    environment: Environment = Environment.Production,
    auto_deploy_option=AutoDeployOption.RELEASE,
    console_log_level=LogLevel.WARNING,
    redirect_console_logs_to_terminal: bool = False,
    application_id: Optional[str] = None,
    executable_name: Optional[str] = None,
    pool_id: str = "",
    inplace_execution: bool = False,
) -> OneWorkflowClient:
    """
    Creates and configures an instance of the OneWorkflowClient for interacting with the
    OneWorkflow system. The client can be used to manage and execute workflows. It is
    typically used at the beginning of your script to create a client instance.

    See the OneWorkflowClient documentation for methods to manage and execute workflows.

    Args:
        cloud_run (bool): A boolean indicating whether the code is running in a cloud context.
        workspace_id (str): The unique identifier for the workspace.
        workspace_path (str): The local path to the workspace directory.
        workspace_common_folder_name (str): Specifies the folder name within `workspace_path` for
            storing files commonly used across the workflow. If not specified, it defaults to
            'CommonFiles'.
        workspace_load_cases_folder_name (str): Specifies the folder name within `workspace_path`
            for storing load cases folders used in the workflow. If not specified, it defaults to
            'LoadCases'.
        workspace_results_folder_name (str): Identifies the folder name within `workspace_path`
            where the output files of the load cases from the workflow run are located. This
            argument identifies the destination folder for these load case results. If not
            specified, it defaults to 'LoadCases'.
        local_workflow_runtime_temp_folder_path (str): The path to a temporary directory for
            storing intermediate data. Defaults to 'C:\\\\Temp\\\\OneWorkflow'.
        local_workflow_runtime_path (str, optional): Specifies the path for the local workflow
            runtime. If not provided, defaults to the 'OneCompute\\\\LocalWorkflowRuntime'
            subdirectory within the '%LOCALAPPDATA%' environment variable on Windows
            (typically 'C:\\\\Users\\\\<username>\\\\AppData\\\\Local').
        local_workflow_runtime_service_visible (bool, optional): A boolean flag indicating whether
            the LocalWorkflowRuntime service should run with or without a visible console window.
            Defaults to False, indicating that the console window is not visible.
        local_workflow_runtime_temp_folders_cleanup (bool, optional): Specifies whether the
            LocalWorkflowRuntime service should remove temporary directories upon shutdown. Default
            behavior is True, indicating cleanup will occur.
        platform (Platform, optional): The target platform for workflow execution.
            Default is Platform.WINDOWS.
        max_cores (int, optional): The maximum number of CPU cores to use for execution.
            If not specified, the client will use the system's available CPU cores.
        debug_local_worker (bool, optional): Enable debugging mode for the local worker if True.
            Default is False.
        local_worker_host_apps_path (str, optional): The path to host applications for local
            worker execution. Default is an empty string, indicating that the applications will
            be retrieved automatically.
        environment (Environment): The cloud environment in which workflows will be executed.
            Defaults to 'Environment.Production'.
        auto_deploy_option (AutoDeployOption): The auto deploy option for the applications.
            Defaults to "RELEASE".
        console_log_level (LogLevel, optional): The log level for console messages.
            Defaults to LogLevel.WARNING.
        redirect_console_logs_to_terminal (bool): Flag indicating whether to redirect console logs
            to the terminal. Default to False.
        application_id (Optional[str]): A unique identifier for the application. This ID is used to
            differentiate the application in various execution contexts (local or cloud) and
            platforms. In a local context, it aligns with the ID of the local worker host executable
            , as defined in the OneCompute Manifest (OCM) file within the local workflow runtime
            package and defaults to "OneWorkflowWorkerHost" if not specified. In a cloud context,
            it signifies the OneCompute application ID and defaults to "OneWorkflowWorkerLinux" for
            Linux and "OneWorkflowWorkerWindows" for Windows if not specified.
        executable_name (Optional[str]): Specifies the name of the worker host executable to be run.
            If not provided, it defaults to an empty string for local execution, indicating that the
            default local executable should be used. For cloud execution, it defaults to
            "OneWorkflowWorkerHost", the standard executable for cloud-based workflows.
        pool_id (str, optional): The ID of the pre-configured pool on the cloud. This pool, a
            collection of nodes with necessary applications, is used for task execution. If not
            specified, the default  pool linked to the application ID on the OneCompute Platform
            is used. If specified, jobs are submitted directly to this pool.
        inplace_execution (bool): Determines the mode of local workflow execution. If True, the
            workflow executes in-place within the `workspace_path`, preserving any changes made
            during execution. If False (default), the workflow executes in a temporary directory
            specified by `local_workflow_runtime_temp_folder_path`, ensuring a clean environment
            and preventing unintended workspace modifications.
    Returns:
        OneWorkflowClient: An instance of the OneWorkflowClient configured with the specified
        parameters.
    """
    application_id = application_id or _oc_application_id(cloud_run, platform)
    executable_name = executable_name or _worker_host_executable_name(cloud_run)

    workflow_client = OneWorkflowClient(
        application_id=application_id,
        pool_id=pool_id,
        local_workflow_runtime_path=local_workflow_runtime_path,
        local_workflow_runtime_temp_folder_path=local_workflow_runtime_temp_folder_path,
        local_workflow_runtime_service_visible=local_workflow_runtime_service_visible,
        local_workflow_runtime_temp_folders_cleanup=local_workflow_runtime_temp_folders_cleanup,
        cloud_run=cloud_run,
        workspace_id=workspace_id,
        workspace_path=workspace_path,
        common_directory=workspace_common_folder_name,
        load_cases_directory=workspace_load_cases_folder_name,
        results_directory=workspace_results_folder_name,
        environment=environment,
        executable_name=executable_name,
        local_worker_host_apps_path=local_worker_host_apps_path,
        debug_local_worker=debug_local_worker,
        console_log_level=console_log_level,
        auto_deploy_option=auto_deploy_option,
        max_concurrent_workers=max_cores,
        redirect_console_logs_to_terminal=redirect_console_logs_to_terminal,
        inplace_execution=inplace_execution,
    )
    return workflow_client


def terminate_background_applications():
    """
    Terminates background applications initiated by all instances of the Local Workflow Runtime
    service.

    This function is designed to terminate background applications that were started by all
    instances of the Local Workflow Runtime service.
    """
    application = "wc.exe" if os_platform.system() == "Windows" else "wc"
    ProcessManager(application).terminate_processes(force=True)


def enable_file_transfer_progress_reporting(ow_client: OneWorkflowClient):
    """
    Enables file transfer progress reporting for the OneWorkflowClient.

    Args:
        ow_client (OneWorkflowClient): The OneWorkflowClient instance to enable file transfer
            progress reporting for.
    """
    if not isinstance(
        ow_client.file_transfer_progress_monitor, FileTransferProgressIndicator
    ):
        ow_client.file_transfer_progress_monitor = FileTransferProgressIndicator()
    ow_client.file_transfer_progress_monitor.enable()


def disable_file_transfer_progress_reporting(ow_client: OneWorkflowClient):
    """
    Disable file transfer progress reporting for the OneWorkflowClient.

    Args:
        ow_client (OneWorkflowClient): The OneWorkflowClient instance to disable file transfer
            progress reporting for.
    """
    if isinstance(
        ow_client.file_transfer_progress_monitor, FileTransferProgressIndicator
    ):
        ow_client.file_transfer_progress_monitor.disable()
