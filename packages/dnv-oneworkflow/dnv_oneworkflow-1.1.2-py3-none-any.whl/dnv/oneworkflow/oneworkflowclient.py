"""
The OneWorkflowClient class in this module acts as a client interface, enabling interaction with 
workflows and offering essential capabilities for creating, executing, and overseeing tasks and 
operations related to workflows. Additionally, it empowers users with the ability to upload files,
download results, create jobs, and submit them for execution, providing comprehensive support for
diverse workflow-related tasks and efficient workflow management.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, ClassVar, Coroutine, List, Optional, Tuple, Union

import dateutil.parser
from dnv.onecompute import (
    Environment,
    IAuthenticator,
    JobEventArgs,
    LocalWorkflowRuntimeServiceManager,
    MSALInteractiveAuthenticator,
    OneComputeClient,
    OneComputeWebApiClientId,
    OneComputeWebApiEndpoints,
    WorkItemEventArgs,
)
from dnv.onecompute.azure_blob_storage_file_service import AzureBlobStorageFileService
from dnv.onecompute.enums import AutoDeployOption, LogLevel
from dnv.onecompute.file_service import FileService, FileTransferOptions, ProgressInfo
from dnv.onecompute.flowmodel import (
    CompositeWork,
    FileTransferSpecification,
    Job,
    ParallelWork,
    SchedulingOptions,
    WorkItem,
    WorkUnit,
)
from dnv.onecompute.host_file_service import HostFileService
from dnv.onecompute.job_info import JobInfo
from dnv.onecompute.job_monitor import IJobMonitor
from dnv.onecompute.work_item_properties import ResultStorageTypes, WorkItemProperties
from dnv.onecompute.work_item_storage_info import WorkItemStorageInfo

# pylint: disable=relative-beyond-top-level
from .config import WorkerConfiguration, WorkspaceConfiguration
from .file_transfer_progress_monitor import FileTransferProgressMonitor
from .job_builder import JobBuilder
from .logging_utils import setup_logger

JobCallback = Callable[[OneComputeClient, JobEventArgs], Coroutine[Any, Any, None]]
WorkItemCallback = Callable[
    [OneComputeClient, WorkItemEventArgs], Coroutine[Any, Any, None]
]


@dataclass
class OneWorkflowClient:
    """
    Represents a client for managing workflows and tasks within the OneWorkflow platform.
    """

    APP_CLIENT_ID: ClassVar[str] = "ba335730-4e2e-4432-9076-a308b0830af1"
    """
    The client ID registered with Veracity for the application.

    Defaults to "ba335730-4e2e-4432-9076-a308b0830af1", serving as a development and testing
    client application.
    """

    def __init__(
        self,
        application_id: str,
        executable_name: str = "",
        workspace_id: str = "",
        workspace_path: str = "",
        common_directory: str = "CommonFiles",
        load_cases_directory: str = "LoadCases",
        results_directory: str = "Results",
        local_workflow_runtime_endpoint: str = "",
        local_workflow_runtime_path: Optional[str] = None,
        local_workflow_runtime_temp_folder_path: Optional[str] = None,
        local_workflow_runtime_startup_wait_time: int = 5,
        local_workflow_runtime_service_visible: bool = False,
        local_workflow_runtime_log_filename: Optional[str] = None,
        local_workflow_runtime_temp_folders_cleanup: bool = True,
        local_worker_host_apps_path: Optional[str] = None,
        debug_local_worker: bool = False,
        console_log_level: LogLevel = LogLevel.WARNING,
        auto_deploy_option: AutoDeployOption = AutoDeployOption.RELEASE,
        max_concurrent_workers: Optional[int] = None,
        cloud_run: bool = False,
        environment: Environment = Environment.Production,
        authenticator: Optional[IAuthenticator] = None,
        pool_id: str = "",
        job_status_polling_interval: int = 10,
        redirect_console_logs_to_terminal: bool = False,
        logger: Optional[logging.Logger] = None,
        inplace_execution: bool = False,
    ):
        """
        Initialize a client for the OneWorkflow service.

        Args:
            application_id (str): A unique identifier for the application. This ID is utilized to
                distinguish the application in different execution contexts (local or cloud). In a
                local context, it corresponds to the ID of the local worker host executable, as
                specified in the OneCompute Manifest(OCM) file within the local workflow runtime
                package. In a cloud context, it represents the OneCompute application ID.
            executable_name (str): Specifies the name of the worker host executable to be run. If
                not provided, it defaults to an empty string for local execution, indicating that
                the default local executable should be used. For custom execution, it should be the
                name of a valid  executable present in the worker host application directory.
            workspace_id (str, optional): The ID of the workspace associated with the workflow.
                It defaults to a randomly generated UUID if left unset or set to an empty string.
            workspace_path (str, optional): The path to the workspace directory it defaults to the
                current working directory if left unset or set to an empty string.
            common_directory (str, optional): The directory for common files within the workspace.
                Defaults to "CommonFiles".
            load_cases_directory (str, optional): The directory for load cases within the workspace.
                Defaults to "LoadCases".
            results_directory (str, optional): The directory for storing results within the
                workspace. Defaults to "Results".
            local_workflow_runtime_endpoint (str, optional): The endpoint for the local workflow
                runtime service.
            local_workflow_runtime_path (str, optional): The path to the local workflow runtime
                service. Defaults to the 'OneCompute\\\\LocalWorkflowRuntime' subdirectory of
                '%LOCALAPPDATA%' environment variable on Windows, which is typically located at
                'C:\\\\Users\\\\<username>\\\\AppData\\\\Local'.
            local_workflow_runtime_temp_folder_path (str, optional): The path to a temporary folder
                used by the local workflow runtime. If not provided, a system-dependent default
                directory is used. On Windows, this is typically within the '%TEMP%' directory
                ('$userprofile\\\\AppData\\\\Local\\\\Temp'). On Linux, it's often within '/tmp'.
            local_workflow_runtime_startup_wait_time (int, optional): The wait time (in seconds)
                after starting the local workflow runtime. Defaults to 5 seconds.
            local_workflow_runtime_service_visible (bool, optional): A boolean flag indicating
                whether the LocalWorkflowRuntime service should run with or without a visible
                console window. Defaults to False, indicating that the console window is not
                visible.
            local_workflow_runtime_log_filename (str, optional): The filename for the local workflow
                runtime log. Defaults to 'wc.log'
            local_workflow_runtime_temp_folders_cleanup (bool, optional): Specifies whether the
                LocalWorkflowRuntime service should remove temporary directories upon shutdown.
                Defaults to True, signifying that cleanup will take place. However, if
                `inplace_execution` is True, this flag will be ignored as the workflow runs in the
                specified workspace and no temporary directories are created.
            local_worker_host_apps_path (str, optional): The path to host applications for local
                workers. Defaults to the 'OneCompute\\\\OneWorkflowWorkerHost' subdirectory of
                '%LOCALAPPDATA%' environment variable on Windows, which is typically located at
                'C:\\\\Users\\\\<username>\\\\AppData\\\\Local'
            debug_local_worker (bool): Indicates whether to run local workers in debug mode.
                Defaults to False.
            console_log_level (LogLevel, optional): The log level for console messages.
                Defaults to LogLevel.WARNING.
            auto_deploy_option (AutoDeployOption, optional): The auto-deploy option for workflow
                tasks. Defaults to AutoDeployOption.RELEASE.
            max_concurrent_workers (int, optional): The maximum number of concurrent workers
                allowed, if specified. Default to use all the cores.
            cloud_run (bool, optional): Indicates whether workflows should be executed in the cloud.
                Defaults to False.
            environment (Environment): The cloud environment in which workflows will be executed.
                Defaults to 'Environment.Production'.
            authenticator (IAuthenticator, optional): An authenticator for the client, if provided.
            pool_id (str, optional): The ID of the pre-configured pool on the cloud. This pool, a
                collection of nodes with necessary applications, is used for task execution. If not
                specified, the default  pool linked to the application ID on the OneCompute Platform
                is used. If specified, jobs are submitted directly to this pool. Defaults to an
                empty string.
            job_status_polling_interval (int, optional): The polling interval (in seconds) for
                checking job status. Defaults to 10 seconds.
            redirect_console_logs_to_terminal (bool): Flag indicating whether to redirect console
                logs to the terminal. Default to False.
            logger (Optional[Logger]): This logger is used for logging messages or errors that may
                occur during the workflow execution. If not provided (None), a new logger is created
                with the name of this class, and its default log level is set to INFO.
                The log level can be adjusted either by using the `setLevel()` method on the logger
                instance obtained via `logging.getLogger("OneWorkflowClient")`, or by employing
                `logging.basicConfig`.
            inplace_execution (bool): Determines the mode of local workflow execution. If True, the
                workflow executes in-place within the `workspace_path`, preserving any changes made
                during execution. If False (default), the workflow executes in a temporary directory
                specified by `local_workflow_runtime_temp_folder_path`, ensuring a clean environment
                and preventing unintended workspace modifications.
        """
        self._logger = setup_logger(self.__class__.__name__, logger)

        self.application_id: str = application_id
        self.executable_name: str = executable_name
        self.workspace_id: str = workspace_id
        self.workspace_path: str = workspace_path
        self.common_directory: str = common_directory
        self.load_cases_directory: str = load_cases_directory
        self.results_directory: str = results_directory
        self.local_workflow_runtime_endpoint: str = local_workflow_runtime_endpoint
        self.local_workflow_runtime_path: Optional[str] = local_workflow_runtime_path
        stripped_path = (
            local_workflow_runtime_temp_folder_path.strip()
            if local_workflow_runtime_temp_folder_path
            else ""
        )
        self.local_workflow_runtime_temp_folder_path = (
            stripped_path if stripped_path else None
        )
        self.local_workflow_runtime_startup_wait_time: int = (
            local_workflow_runtime_startup_wait_time
        )
        self.local_workflow_runtime_service_visible: bool = (
            local_workflow_runtime_service_visible
        )
        self.local_workflow_runtime_log_filename: Optional[str] = (
            local_workflow_runtime_log_filename
        )
        self.local_workflow_runtime_temp_folders_cleanup: bool = (
            local_workflow_runtime_temp_folders_cleanup
        )
        self.local_worker_host_apps_path: Optional[str] = local_worker_host_apps_path
        self.debug_local_worker: bool = debug_local_worker
        self.console_log_level: LogLevel = console_log_level
        self.auto_deploy_option: AutoDeployOption = auto_deploy_option
        self.max_concurrent_workers: Optional[int] = max_concurrent_workers
        self.cloud_run: bool = cloud_run
        self.environment: Environment = environment
        self.authenticator: Optional[IAuthenticator] = authenticator
        self.pool_id: str = pool_id
        self.job_status_polling_interval: int = job_status_polling_interval
        self.redirect_console_logs_to_terminal: bool = redirect_console_logs_to_terminal
        self.inplace_execution: bool = inplace_execution
        self.file_transfer_progress_monitor: Optional[FileTransferProgressMonitor] = (
            _LogFileTransferInfo(self._logger)
        )
        self._local_workflow_runtime_service: Optional[
            LocalWorkflowRuntimeServiceManager
        ] = None
        self._one_compute_client: Optional[OneComputeClient] = None
        self._workspace_config: Optional[WorkspaceConfiguration] = None
        self._worker_config: Optional[WorkerConfiguration] = None
        self.__post_init__()

    def __post_init__(self):
        """
        Perform any post-initialization actions for the OneWorkflowClient.
        """
        if not self.workspace_id.strip():
            self.workspace_id = str(uuid.uuid4())

        if not self.workspace_path.strip():
            self.workspace_path = os.getcwd()

        if not self.common_directory.strip():
            self.common_directory = "CommonFiles"

        if not self.load_cases_directory.strip():
            self.load_cases_directory = "LoadCases"

        if not self.results_directory.strip():
            self.results_directory = "Results"

        self.local_workflow_runtime_path = (
            self.local_workflow_runtime_path
            if self.local_workflow_runtime_path
            else os.path.join(
                os.environ["LOCALAPPDATA"],
                "OneCompute",
                "LocalWorkflowRuntime",
                "wc.exe",
            )
        )

        self.local_worker_host_apps_path = (
            self.local_worker_host_apps_path
            if self.local_worker_host_apps_path
            else os.path.join(os.environ["LOCALAPPDATA"], "OneCompute")
        )
        if not os.path.exists(self.local_worker_host_apps_path):
            os.makedirs(self.local_worker_host_apps_path, exist_ok=True)

        self._workspace_config = WorkspaceConfiguration(
            workspace_id=self.workspace_id,
            workspace_path=self.workspace_path,
            common_files_directory=self.common_directory,
            load_cases_parent_directory=self.load_cases_directory,
            results_directory=self.results_directory,
        )

        self._worker_config = WorkerConfiguration(
            command=self.executable_name,
            service_name=self.application_id,
            pool_id=self.pool_id,
        )

        if not (
            self.local_workflow_runtime_log_filename
            and self.local_workflow_runtime_log_filename.strip()
        ):
            # Generate a unique log filename to allow multiple instances of the local workflow
            # runtime service to run simultaneously. This prevents file lock issues by ensuring
            # each instance writes to its own unique log file. The filename includes the current
            # date and time down to microseconds ('%Y_%m_%d_%H_%M_%S_%f') to ensure uniqueness.
            self.local_workflow_runtime_log_filename = os.path.join(
                self.workspace_path,
                f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}_wc.log",
            )

        if not self.cloud_run:
            self._initialize_local_workflow_runtime_service()

        self._initialize_one_compute_client()

    def start_workflow_runtime_service(self):
        """
        Starts the workflow runtime service when not running in a cloud environment.
        """
        if self._local_workflow_runtime_service:
            self._local_workflow_runtime_service.start_service()

    def stop_workflow_runtime_service(self):
        """
        Stops the running instance of the workflow runtime service.

        This method is typically used to stop the workflow runtime service when it's no longer
        needed.
        """
        if self._local_workflow_runtime_service:
            self._local_workflow_runtime_service.stop_service()

    @property
    def onecompute_client(self) -> OneComputeClient | None:
        """
        Returns an instance of the OneComputeClient class for interacting with the compute platform.

        Returns:
            OneComputeClient: An instance of the OneComputeClient class or None if not initialized.
        """
        return self._one_compute_client

    @property
    def workspace_info(self) -> WorkspaceConfiguration | None:
        """
        Returns an instance of the WorkspaceConfiguration class.

        Returns:
            WorkspaceConfiguration: An instance of the WorkspaceConfiguration class or None
            otherwise.
        """
        return self._workspace_config

    @property
    def local_workflow_runtime_service(
        self,
    ) -> LocalWorkflowRuntimeServiceManager | None:
        """
        Returns an instance of LocalWorkflowRuntimeServiceManager.

        Returns:
            An instance of LocalWorkflowRuntimeServiceManager class.
        """
        return self._local_workflow_runtime_service

    @property
    def job_root_directory(self) -> Optional[str]:
        """
        Gets the root directory of the job.

        This property retrieves the root directory of the job, which is created and managed by the
        local workflow runtime service. This is the directory where the workspace folder is created.

        Returns:
            Optional[str]: The root directory of the job, if available; otherwise, None.
        """
        job_working_dir = (
            self._local_workflow_runtime_service.get_job_working_path()
            if self._local_workflow_runtime_service
            else None
        )
        if job_working_dir:
            return (
                os.path.dirname(job_working_dir)
                if os.path.basename(job_working_dir) == self.workspace_id
                else job_working_dir
            )
        return None

    @property
    def blob_root_directory(self) -> Optional[str]:
        """
        Gets the root directory for blob storage.

        This property returns the path to the root directory for blob storage. This directory is
        managed by the local workflow runtime service. If the service is not available, the method
        returns None.

        Returns:
            Optional[str]: The path to the root directory for blob storage, or None if the service
            is not available.
        """
        return (
            self._local_workflow_runtime_service.get_blob_storage_path()
            if self._local_workflow_runtime_service
            else None
        )

    def upload_files_from_directory(
        self,
        directory: Optional[str],
        subdirectory: Optional[str],
        file_options: Optional[FileTransferOptions],
        is_recursive: bool = False,
    ) -> bool:
        """
        Uploads files from a specified directory or subdirectory to the Standard storage of the
        OneCompute platform.

        Args:
            directory (Optional[str]): The full path of the directory from which files are to be
                uploaded. If not specified, the method will skip the file upload and return True.
            subdirectory (Optional[str]): The name of the subdirectory within the specified
                directory from which files are to be uploaded. If not specified, the method will
                skip the file upload and return True.
            file_options (Optional[FileTransferOptions]): The file options for filtering files.
                Default value is None.
            is_recursive (bool): If True, files from each subdirectory of the specified directory
                are uploaded. Default value is False.
        Returns:
            bool: Returns True if the upload was successful, or if there were no files to upload
            due to a default, missing, or incorrect configuration. Returns False if the upload
            failed or the directory was invalid.
        """
        if not self._validate_file_upload_path_inputs(directory, subdirectory):
            return True

        assert subdirectory is not None
        directories_to_upload = (
            [os.path.join(subdirectory, d) for d in os.listdir(directory)]
            if is_recursive
            else [subdirectory]
        )

        for dir_to_upload in directories_to_upload:
            try:
                self._upload_files(dir_to_upload, file_options)
            except Exception as ex:
                self._logger.error(
                    "An error occurred while attempting to upload files from %s. Details: %s.",
                    dir_to_upload,
                    ex,
                )
                return False
        return True

    def login(self) -> bool:
        """
        Authenticates the user with the OneCompute platform service.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        if self.cloud_run and self.authenticator:
            try:
                self.authenticator.authenticate()
                return True
            except Exception as ex:
                self._logger.error(
                    "Login failed due to an authentication error: %s", str(ex)
                )
        return False

    def upload_files(
        self,
        common_files: bool = True,
        input_files: bool = True,
        file_options: Optional[FileTransferOptions] = None,
    ) -> bool:
        """
        Uploads common and input files to OneCompute's Standard storage, unless the workflow is set
        to execute in-place, in which case it immediately returns True, skipping the upload.

        Args:
            common_files (bool): Indicates whether to upload common files. Default value is True.
            input_files (bool): Indicates whether to upload input files. Default value is True.
            file_options (Optional[FileTransferOptions]): The file options for filtering files.
                Default value is None.

        Returns:
            bool: Returns True if files are successfully uploaded or if in-place execution is set,
            otherwise False.
        """
        if self.inplace_execution:
            return True
        if common_files and not self.upload_common_files(file_options):
            return False
        if input_files and not self.upload_input_files(file_options):
            return False
        return True

    def upload_common_files(
        self, file_options: Optional[FileTransferOptions] = None
    ) -> bool:
        """
        Uploads common files to OneCompute's Standard storage, unless the workflow is set for
        in-place execution, in which case it immediately returns True, skipping the upload.

        Returns:
            bool: True if files are successfully uploaded or if in-place execution is set,
            otherwise False if the upload operation fails or the workspace configuration is
            invalid.
        """
        if self.inplace_execution:
            return True

        workspace = self._workspace_config
        if not self._validate_workspace(workspace):
            return False

        assert workspace is not None
        return self.upload_files_from_directory(
            directory=workspace.common_files_fullpath,
            subdirectory=workspace.common_files_directory,
            file_options=file_options,
        )

    def upload_input_files(
        self, file_options: Optional[FileTransferOptions] = None
    ) -> bool:
        """
        Uploads input files to OneCompute's Standard storage, unless the workflow is set for
        in-place execution, in which case it immediately returns True, skipping the upload.

        Returns:
            bool: True if files are successfully uploaded or if in-place execution is set,
            otherwise False if the upload operation fails or the workspace configuration is
            invalid.
        """
        if self.inplace_execution:
            return True

        workspace = self._workspace_config
        if not self._validate_workspace(workspace):
            return False

        assert workspace is not None
        return self.upload_files_from_directory(
            directory=workspace.load_cases_fullpath,
            subdirectory=workspace.load_cases_parent_directory,
            file_options=file_options,
            is_recursive=True,
        )

    def upload_result_files(
        self, file_options: Optional[FileTransferOptions] = None
    ) -> bool:
        """
        Uploads results files to OneCompute's Standard storage, unless the workflow is set for
        in-place execution, in which case it immediately returns True, skipping the upload.

        Returns:
            bool: True if files are successfully uploaded or if in-place execution is set, otherwise
            False if the upload operation fails or the workspace configuration is invalid.
        """
        if self.inplace_execution:
            return True

        workspace = self._workspace_config
        if not self._validate_workspace(workspace):
            return False

        assert workspace is not None
        return self.upload_files_from_directory(
            directory=workspace.results_fullpath,
            subdirectory=workspace.results_directory,
            file_options=file_options,
            is_recursive=True,
        )

    def delete_workspace_container(
        self,
    ):
        """
        Deletes the workspace folder and its contents from the OneCompute Standard Storage BLOB
        container. This method uses the `workspace_id` from the workspace configuration to identify
        the directory to delete.
        """
        if self._workspace_config:
            file_service = self._get_file_service()
            if file_service:
                file_service.delete_dir(self._workspace_config.workspace_id)

    async def run_workflow_async(
        self,
        work: ParallelWork | WorkUnit | WorkItem,
        job_preparation_work: Optional[WorkUnit] = None,
        job_release_work: Optional[WorkUnit] = None,
        log_job: bool = False,
        scheduling_options: Optional[SchedulingOptions] = None,
        job_status_changed: Optional[JobCallback] = None,
        job_progress_changed: Optional[JobCallback] = None,
        work_item_status_changed: Optional[WorkItemCallback] = None,
        work_item_progress_changed: Optional[WorkItemCallback] = None,
    ) -> str | None:
        """
        Runs the specified work item asynchronously.

        Args:
            work (ParallelWork | WorkUnit | WorkItem): The main work to be processed in the
                workflow.
            job_preparation_work (Optional[WorkUnit]): An optional work unit representing the
                preparation steps before the main work unit is processed.
            job_release_work (Optional[WorkUnit]): An optional work unit representing the
                post-processing steps after the main work unit is processed.
            log_job (bool, optional): Flag to indicate whether to log job information.
                Defaults to False.
            scheduling_options (Optional[SchedulingOptions]): Additional options for scheduling the
                workflow. Defaults to None.
            job_status_changed (Optional[JobCallback]): A callback function triggered when the job
                status changes. Defaults to None.
            job_progress_changed (Optional[JobCallback]): A callback function triggered when the job
                progress changes. Defaults to None.
            work_item_status_changed (WorkItemCallback): A callback function triggered when the work
                item status changes. Defaults to None.
            work_item_progress_changed (WorkItemCallback): A callback function triggered when the
                work item progress changes. Defaults to None.

        Returns:
            The ID of the job created for the work item, or None if the job could not be created or
            failed to execute.

        Raises:
            Any appropriate exceptions raised during the workflow execution.

        Notes:
            This method is intended for the asynchronous execution of a workflow, where each work
            item represents a task to be completed within the workflow.
            The 'jobPreparation' and 'jobRelease' arguments can be used to specify any preparation
            or post-processing steps related to the main work.
        """
        try:
            if not self.onecompute_client:
                return None

            job = self.create_job(
                work,
                job_preparation_work=job_preparation_work,
                job_release_work=job_release_work,
                scheduling_options=scheduling_options,
            )
            if job is None:
                return None

            if log_job:
                job_json = json.dumps(job, default=lambda o: o.encode(), indent=4)
                self._logger.info("Job JSON: %s", job_json)

            job_monitor = await self.onecompute_client.submit_job_async(job)
            jsc = job_monitor.job_status_changed
            jsc += (
                job_status_changed if job_status_changed else self._job_status_changed
            )

            jpc = job_monitor.job_progress_changed
            jpc += (
                job_progress_changed
                if job_progress_changed
                else self._job_progress_changed
            )

            wisc = job_monitor.work_item_status_changed
            wisc += (
                work_item_status_changed
                if work_item_status_changed
                else self._work_item_status_changed
            )

            wipc = job_monitor.work_item_progress_changed
            wipc += (
                work_item_progress_changed
                if work_item_progress_changed
                else self._work_item_progress_changed
            )

            await job_monitor.await_job_termination_async()
            return job.JobId
        except Exception as ex:
            self._logger.error("An exception occurred: %s", ex)
        return None

    def create_job(
        self,
        work: ParallelWork | WorkUnit | WorkItem,
        job_preparation_work: Optional[WorkUnit] = None,
        job_release_work: Optional[WorkUnit] = None,
        scheduling_options: Optional[SchedulingOptions] = None,
    ) -> Job | None:
        """
        Creates a new job for the given work item and returns a 'Job' object.

        Args:
            work (ParallelWork | WorkUnit | WorkItem): The main work to be processed in the
                workflow.
            job_preparation_work (Optional[WorkUnit]): An optional work unit representing the
                reparation steps before the main work item is processed.
            job_release_work (Optional[WorkUnit]): An optional work unit representing the
                post-processing steps after the main work item is processed.
            scheduling_options (Optional[SchedulingOptions]): The scheduling options for the
                workflow.

        Returns:
            The ID of the job created for the work item, or None if the job could not be created or
            failed to execute.

        Notes:
            This method is intended for the asynchronous execution of a workflow, where each work
            item represents a task to be completed within the workflow.
            The 'jobPreparation' and 'jobRelease' arguments can be used to specify any preparation
            or post-processing steps related to the main work.
        """
        if any(
            (
                self._workspace_config is None,
                self.onecompute_client is None,
                self._worker_config is None,
            )
        ):
            return None

        job_builder = JobBuilder(
            self.onecompute_client,  # type: ignore
            self._workspace_config,  # type: ignore
            self._worker_config,  # type: ignore
            self.cloud_run,
            self.inplace_execution,
        )
        try:
            job = job_builder.create_job(
                work,
                job_preparation_work,
                job_release_work,
                scheduling_options,
            )
            return job
        except Exception as ex:
            self._logger.error("An exception occurred: %s", ex)
        return None

    def submit_job(self, job: Job) -> str | None:
        """
        Submits a job to the OneCompute platform.

        Args:
            job (Job): The job to be submitted.

        Returns:
            str | None: The ID of the submitted job or None if submission failed.

        """
        return (
            self.onecompute_client.submit_job(job) if self.onecompute_client else None
        )

    async def submit_job_async(self, job: Job) -> IJobMonitor | None:
        """
        Asynchronously submits a job to the OneCompute platform.

        Args:
            job (Job): The job to be submitted.

        Returns:
            IJobMonitor: An object that can be used to monitor the status of the job.
        """
        return (
            await self.onecompute_client.submit_job_async(job)
            if self.onecompute_client
            else None
        )

    def download_job_logs(
        self, job_info: str | Job, work_item_id: str = "", download_folder: str = ""
    ):
        """
        Downloads the logs for a specified job from the OneCompute platform's Standard storage,
        unless the workflow is set for in-place execution, in which case it immediately returns
        None, skipping the download.

        This method facilitates the download of logs for a designated job from the OneCompute
        platform's Standard storage. The method's input can be the Job's ID or a Job object.
        Furthermore, there is an option to specify a work item ID for downloading logs for a
        particular work item within the Job. If a work item ID is not provided, the method will
        download logs for all work items associated with the Job by default. An optional parameter
        allows for the specification of a local folder path for saving the logs. If no folder path
        is specified, the logs will be downloaded to the Results folder of the workspace.

        Args:
            job_info (str or Job): The job's ID or a Job object for specifying the job to download
                logs for.
            work_item_id (str): An optional parameter specifying the work item ID. It defaults to an
                empty string, which means that logs for all work items associated with the specified
                Job will be downloaded unless provided.
            download_folder (str): An optional parameter for indicating the local folder path to
                save the logs. If not specified, the logs will be downloaded to the Results folder
                of the workspace.
        """
        if self.inplace_execution:
            return None

        if not self.onecompute_client or not self._workspace_config:
            return

        job_execution_info = self._get_job_execution_info(job_info)
        if job_execution_info is None:
            self._logger.error("Failed to fetch the job info")
            return

        # If a work item (like ParallelWork) does not have a parent, there is no need to perform
        # any further actions. This prevents unnecessary operations such as downloading non-existent
        # logs, which is typical for work items without parents.
        work_item_properties = self._get_workitem_properties(
            job_execution_info.JobId, work_item_id
        )
        if work_item_properties and work_item_properties.ParentId == "":
            return

        job_logs_folder = self._get_job_logs_folder(job_execution_info)
        work_item_folder_mapping = self._get_work_item_folder_mapping(
            job_info, work_item_id
        )

        for wi_id, wi_folder in work_item_folder_mapping.items():
            self._download_work_item_log_files(
                job_logs_folder, wi_id, wi_folder, download_folder
            )

    async def download_job_results_async(
        self, job_id: str, filename: str = "results.txt"
    ) -> str:
        """
        Downloads the results for a specified job and saves them to a text file, unless the workflow
        is set for in-place execution, in which case it immediately returns an empty string,
        bypassing the download.

        Args:
            job_id (str): The ID of the job whose results to download.
            filename (str): The filename is optional and specifies the name of the output file.
                If not provided, the output file will have the default name which is "results.txt".

        Returns:
            str: The full path of the directory where the job results were downloaded or an empty
            string if the job results could not be downloaded or if the workflow is set for in-place
            execution.

        Raises:
            IOError: If an error occurs while writing the job results.
        """
        if self.inplace_execution:
            return ""

        assert self.onecompute_client is not None
        results = await self.onecompute_client.get_workitem_results_async(job_id)
        if not results:
            return ""

        assert self._workspace_config is not None
        for result in results:
            results_path = os.path.join(
                self._workspace_config.results_fullpath, result.WorkItemId
            )
            os.makedirs(results_path, exist_ok=True)

            result_file = os.path.join(results_path, filename)
            try:
                with open(result_file, "w", encoding="utf-8") as file:
                    self._logger.info("The result file is '%s'", result_file)
                    if result.Data.Content and isinstance(result.Data.Content, str):
                        file.write(result.Data.Content)
            except IOError as ex:
                self._logger.error(
                    "Failed to write results to file for job '%s' and work item '%s': %s",
                    job_id,
                    result.WorkItemId,
                    ex,
                )
        return self._workspace_config.results_fullpath

    async def download_result_files_async(
        self,
        job_id: str,
        workitem_id: str = "",
        file_options: Optional[FileTransferOptions] = None,
    ) -> list[str]:
        """
        Downloads the result files for a job's work item. Skips the download if the workflow is
        configured for in-place execution.

        This function downloads the result files for a specific work item in a job. The workitem_id
        parameter can be used to specify the work item whose results are to be downloaded. If a work
        item ID is not specified, the function will download results for all work items in the job.

        The file_options parameter can be used to filter the files that are downloaded. For instance
        , it can be used to download only files of a certain type, or files of certain size.

        Args:
            job_id (str): The ID of the job that contains the work item.
            workitem_id (str, optional): The ID of the work item for which to download the results.
                If not specified, results for all work items in the job will be downloaded.
                Defaults to "".
            file_options (Optional[FileTransferOptions]): The options for filtering which files to
                download.Default value is None.

        Returns:
            list[str]: Returns a list of paths to the downloaded files. For in-place execution or
            when no files are downloaded, an empty list is returned.
        """
        if self.inplace_execution:
            return []

        (
            work_items_properties,
            container_name,
        ) = await self._get_properties_and_container_name(job_id, workitem_id)

        if not (container_name and work_items_properties):
            self._logger.error(
                "Failed to fetch necessary data for job '%s'. Please try again later.",
                job_id,
            )
            return []

        work_items_properties = self._filter_properties(
            work_items_properties, workitem_id
        )

        if not work_items_properties:
            return []

        storage_info, container_url = await self._get_storage_info_and_container_url(
            job_id, container_name
        )

        work_items_info = self._get_work_items_info(
            job_id, work_items_properties, storage_info, container_url
        )

        return (
            await self._download_results_async(work_items_info, file_options)
            if work_items_info
            else []
        )

    async def _get_properties_and_container_name(self, job_id: str, workitem_id: str):
        """
        Asynchronously retrieves the properties of a work item and the name of its container.

        Args:
            job_id (str): The ID of the job that contains the work item.
            workitem_id (str): The ID of the work item.

        Returns:
            tuple: A tuple containing the work item properties and the container name.
        """
        assert self.onecompute_client is not None
        return await asyncio.gather(
            self.onecompute_client.get_workitem_properties_async(job_id, workitem_id),
            self._container_name_async(),
        )

    def _filter_properties(
        self, work_items_properties: List[WorkItemProperties], workitem_id: str
    ) -> Union[List[WorkItemProperties], None]:
        """
        Filters the provided work item properties based on the given work item ID.

        If a work item ID is provided, the function returns a list containing only the properties of
        the work item with that ID. If no work item ID is provided, the function returns all work
        item properties.

        Args:
            work_items_properties (List[WorkItemProperties]): The list of work item properties to
                filter. workitem_id (str): The ID of the work item to filter by.

        Returns:
            List[WorkItemProperties] or None: A list of filtered work item properties, or None if no
            match is found.
        """
        return (
            next(([p] for p in work_items_properties if p.Id == workitem_id), None)
            if workitem_id
            else work_items_properties
        )

    async def _get_storage_info_and_container_url(
        self, job_id: str, container_name: str
    ) -> Tuple[List[WorkItemStorageInfo], str]:
        """
        Retrieves the storage information for a given job and container, and the standard storage
        container URL.

        Args:
            job_id (str): The ID of the job.
            container_name (str): The name of the container.

        Returns:
            Tuple[List[WorkItemStorageInfo], str]: A tuple containing a list of WorkItemStorageInfo
            objects and the standard storage container URL.
        """
        assert self.onecompute_client is not None
        return await asyncio.gather(
            self.onecompute_client.get_workitem_storage_info_async(
                job_id, container_name
            ),
            self._standard_storage_container_url_async(),
        )

    def _get_work_items_info(
        self,
        job_id: str,
        work_items_properties: List[WorkItemProperties],
        storage_info: List[WorkItemStorageInfo],
        default_container_url: str,
    ) -> List[_WorkItemResultStorageInfo]:
        """
        Generates a list of _WorkItemResultStorageInfo objects for each work item in a job.

        This method iterates over the provided work item properties, extracts relevant information,
        and creates a _WorkItemResultStorageInfo object for each work item. These objects are then
        returned in a list.

        Args:
            job_id (str): The ID of the job.
            work_items_properties (List[WorkItemProperties]): The properties of the work items.
            storage_info (List[WorkItemStorageInfo]): The storage information for the work items.
                default_container_url (str): The default container URL.

        Returns:
            List[_WorkItemResultStorageInfo]: A list of _WorkItemResultStorageInfo objects.
        """
        work_items_info = []
        for prop in work_items_properties:
            work_item_directory = prop.WorkItemDirectory.strip()
            if not work_item_directory:
                continue

            work_item_results_subpath = self._extract_path_after(
                work_item_directory, self.results_directory
            )

            work_item_name = os.path.basename(work_item_directory)
            wi_si = next(
                (si for si in storage_info if si.WorkItemId == work_item_name), None
            )
            is_result_lake = prop.ResultStorageType == ResultStorageTypes.ResultLake
            container_url = (
                wi_si.ContainerUri
                if wi_si and is_result_lake
                else default_container_url
            )

            work_items_info.append(
                _WorkItemResultStorageInfo(
                    job_id=job_id,
                    work_item_name=work_item_name,
                    work_item_results_subpath=work_item_results_subpath,
                    container_url=container_url,
                    is_result_lake=is_result_lake,
                )
            )
        return work_items_info

    def _upload_files(
        self,
        file_relative_path: str,
        file_options: Optional[FileTransferOptions] = None,
    ):
        """Uploads files to the OneCompute platform's Standard storage area.

        Args:
            file_relative_path (str): The relative path of the file or the folder containing the
                file.
            file_options (Optional[FileTransferOptions]): The file options for filtering files.
                Default value is None.
        """
        if not self._workspace_config or not self.onecompute_client:
            return

        src_file_abs_path = os.path.join(
            self._workspace_config.workspace_path, file_relative_path
        )
        dst_file_rel_path_in_blob = os.path.join(
            self._workspace_config.workspace_id, file_relative_path
        ).replace(os.sep, "/")

        file_service = self._get_file_service()
        if file_service:
            file_service.upload(
                src_file_abs_path, dst_file_rel_path_in_blob, file_options
            )

    async def _download_results_async(
        self,
        work_items_info: list[_WorkItemResultStorageInfo],
        file_options: Optional[FileTransferOptions] = None,
    ) -> list[str]:
        """
        Downloads the results for the specified list of load case folders returns the path
        or paths to the downloaded files.

        Args:
            work_items_info (list[_WorkItemResultStorageInfo]): A list of work item info for which to
                download results.
            file_options (Optional[FileTransferOptions]): The file options for filtering files.
                Default value is None.
        Returns:
            list[str]: The path or paths to the downloaded files.
        """
        # Use asyncio.ensure_future to download files concurrently
        tasks = [
            asyncio.ensure_future(
                self._download_files_wrapper(
                    wii,
                    file_options,
                )
            )
            for wii in work_items_info
        ]
        results = list[str]()
        for idx, task in enumerate(tasks):
            try:
                downloaded_dir = (await task).result()
                results.append(downloaded_dir)
            except FileNotFoundError as fnf:
                self._logger.error(
                    "Error: %s '%s' for the load-case '%s'",
                    fnf.strerror,
                    fnf.filename,
                    work_items_info[idx].work_item_name,
                )
            except Exception as ex:
                self._logger.error("An exception occurred: %s", ex)
        return results

    async def _download_files_wrapper(
        self,
        wii: _WorkItemResultStorageInfo,
        file_options: Optional[FileTransferOptions] = None,
    ) -> Future[str]:
        future: Future[str] = Future()
        if not self._workspace_config or not self.onecompute_client:
            future.set_result("")
            return future
        try:
            workspace = self._workspace_config
            workspace_id = wii.job_id if wii.is_result_lake else workspace.workspace_id
            results_dir = "" if wii.is_result_lake else workspace.results_directory
            work_item_results_subpath = (
                "" if wii.is_result_lake else wii.work_item_results_subpath
            )

            src_folder_rel_path_in_blob_storage = os.path.join(
                workspace_id, results_dir, work_item_results_subpath
            ).replace(os.sep, "/")

            results_dir = workspace.results_directory
            dst_folder_abs_path_in_local_storage = os.path.join(
                workspace.workspace_path, results_dir, work_item_results_subpath
            )

            # Inform the user about the download initiation
            src_file_uri = (
                f"{wii.container_url}/{src_folder_rel_path_in_blob_storage}".replace(
                    os.sep, "/"
                )
            )

            self._logger.info(
                "Downloading files from '%s' to '%s'",
                src_file_uri,
                dst_folder_abs_path_in_local_storage,
            )

            file_service = self._get_file_service(wii.container_url)
            if file_service is None:
                self._logger.error("File service is not available.")
                future.set_result("")
                return future

            file_service.download(
                src_folder_rel_path_in_blob_storage,
                dst_folder_abs_path_in_local_storage,
                file_options,
            )

            self._logger.info("Download completed.")

            return_res = (
                os.path.join(dst_folder_abs_path_in_local_storage, wii.work_item_name)
                if wii.is_result_lake
                else dst_folder_abs_path_in_local_storage
            )

            future.set_result(return_res)
        except Exception as ex:
            future.set_exception(ex)
        return future

    def _container_name(self) -> str:
        if not self.onecompute_client:
            return ""
        containers = self.onecompute_client.get_containers()
        return containers[0] if containers else ""

    async def _container_name_async(self) -> str:
        if not self.onecompute_client:
            return ""
        containers = await self.onecompute_client.get_containers_async()
        return containers[0] if containers else ""

    def _standard_storage_container_url(self) -> str:
        container = self._container_name()
        if not container or not self.onecompute_client:
            return ""
        container_uri = self.onecompute_client.get_container_uri(container, 1)
        if container_uri is None:
            return ""
        return container_uri

    async def _standard_storage_container_url_async(self) -> str:
        container = self._container_name()
        if not container or not self.onecompute_client:
            return ""
        container_uri = await self.onecompute_client.get_container_uri_async(
            container, 1
        )
        if container_uri is None:
            return ""
        return container_uri

    def _interactive_auth_provider(self) -> IAuthenticator:
        """
        Returns an authenticator for managing authentication tokens in scenarios where user
        interaction is required, such as via a local browser.

        Returns:
            IAuthenticationProvider: An instance of MSALInteractiveAuthenticator.
        """
        return MSALInteractiveAuthenticator(
            authorization_endpoint="https://login.veracity.com",
            tenant="dnvglb2cprod.onmicrosoft.com",
            policy="B2C_1A_SignInWithADFSIdp",
            app_client_id=self.APP_CLIENT_ID,
            api_client_id=OneComputeWebApiClientId.get_onecompute_webapi_client_id(
                self.environment
            ),
        )

    def _initialize_local_workflow_runtime_service(self):
        """
        Initializes the local workflow runtime service.

        This method sets up the LocalWorkflowRuntimeServiceManager with the appropriate parameters.
        The parameters are determined based on the current state of the `inplace_execution`
        attribute. If `inplace_execution` is True, the workflow will run in the specified workspace
        and no temporary directories will be created. If `inplace_execution` is False, the workflow
        will run in a temporary directory, and the cleanup of these directories will be determined
        by the `local_workflow_runtime_temp_folders_cleanup` attribute.
        """
        self._local_workflow_runtime_service = LocalWorkflowRuntimeServiceManager(
            workspace_id="" if self.inplace_execution else self.workspace_id,
            worker_host_apps_path=self.local_worker_host_apps_path or "",
            workflow_runtime_executable_path=self.local_workflow_runtime_path or "",
            workflow_runtime_service_endpoint=self.local_workflow_runtime_endpoint,
            workflow_runtime_log_level=self.console_log_level,
            workflow_runtime_log_filename=self.local_workflow_runtime_log_filename,
            workflow_debugging=self.debug_local_worker,
            auto_deploy_option=self.auto_deploy_option,
            max_concurrent_workers=self.max_concurrent_workers,
            temp_folder_path=(
                None
                if self.inplace_execution
                else self.local_workflow_runtime_temp_folder_path
            ),
            startup_wait_time=self.local_workflow_runtime_startup_wait_time,
            console_window_visible=self.local_workflow_runtime_service_visible,
            redirect_console_logs_to_terminal=self.redirect_console_logs_to_terminal,
            clean_temporary_directories_on_exit=(
                False
                if self.inplace_execution
                else self.local_workflow_runtime_temp_folders_cleanup
            ),
            blob_storage_path=self.workspace_path if self.inplace_execution else "",
            jobs_root_path=self.workspace_path if self.inplace_execution else "",
        )

    def _initialize_one_compute_client(self):
        """
         Initializes the OneCompute client for the workflow execution.

        Returns:
             None
        """
        if self.cloud_run:
            if self.authenticator is None:
                self.authenticator = self._interactive_auth_provider()

            base_url = OneComputeWebApiEndpoints.get_onecompute_webapi_endpoint(
                self.environment
            )
            authenticator = self.authenticator
        else:
            base_url = (
                (self._local_workflow_runtime_service.workflow_runtime_service_endpoint)
                if self._local_workflow_runtime_service
                and self._local_workflow_runtime_service.workflow_runtime_service_endpoint
                else ""
            )
            authenticator = None

        one_compute_client = OneComputeClient(base_url, authenticator)
        one_compute_client.polling_interval_seconds = self.job_status_polling_interval
        self._one_compute_client = one_compute_client

    def _download_work_item_log_files(
        self, job_logs_folder: str, wi_id: str, wi_folder: str, download_folder: str
    ):
        src_folder_path_in_blob_storage = self._get_src_folder_path_in_blob_storage(
            job_logs_folder, wi_id
        )
        dst_folder_path_in_local_storage = self._get_dst_folder_path_in_local_storage(
            wi_folder, download_folder
        )
        try:
            container_url = self._standard_storage_container_url()
            if container_url:
                file_service = self._get_file_service(container_url)
                if file_service:
                    file_service.download(
                        src_folder_path_in_blob_storage,
                        dst_folder_path_in_local_storage,
                    )
        except FileNotFoundError:
            self._logger.error(
                "No standard output or error logs found for the work unit '%s'", wi_id
            )
        except Exception as exception:
            self._logger.error("An exception occurred: %s", exception)

    def _get_job_execution_info(self, job_info: str | Job) -> Optional[JobInfo]:
        assert self.onecompute_client
        job_id = job_info.JobId if isinstance(job_info, Job) else job_info
        return self.onecompute_client.get_job_status(job_id)

    def _get_job_logs_folder(self, job_status: JobInfo) -> str:
        if self.cloud_run:
            job_folder_name = "_joblogs"
            date = dateutil.parser.parse(job_status.StartTime).strftime("%Y-%m-%d")
            return os.path.join(job_folder_name, date, job_status.JobId)
        return os.path.join(self.workspace_id, "Logs")

    def _get_src_folder_path_in_blob_storage(
        self, job_logs_folder: str, work_item_id: str
    ) -> str:
        # Paths in blob storage should always use forward slashes (/) as separators, regardless
        # of the operating system. So, the .replace(os.sep, "/") part is replacing the
        # system-specific path separator with a forward slash. This ensures that the path is
        # correctly formatted for blob storage.
        src_folder_path_in_blob_storage = os.path.join(
            job_logs_folder, work_item_id
        ).replace(os.sep, "/")
        return src_folder_path_in_blob_storage

    def _get_dst_folder_path_in_local_storage(
        self, wi_folder: str, download_folder: str
    ) -> str:
        if not download_folder.strip():
            assert self._workspace_config
            workspace_path = self._workspace_config.workspace_path
            return os.path.join(workspace_path, wi_folder)
        return download_folder

    def _get_work_item_folder_mapping(
        self, job_info: str | Job, work_item_id: str = ""
    ) -> dict[str, str]:
        if isinstance(job_info, Job):
            return self._get_work_items_id_folder_mapping(job_info)
        job_id = job_info
        return self._get_work_items_id_folder_mapping_using_job_id(job_id, work_item_id)

    def _get_work_items_id_folder_mapping_using_job_id(
        self, job_id: str, work_item_id: Optional[str] = None
    ) -> dict[str, str]:
        if not self._workspace_config or not self.onecompute_client:
            return {}

        results_dir = self._workspace_config.results_directory
        work_item_folder_mapping = {}

        work_item_properties = self.onecompute_client.get_workitem_properties(
            job_id, work_item_id or ""
        )

        if not work_item_properties:
            return work_item_folder_mapping

        for prop in work_item_properties:
            work_item_directory = prop.WorkItemDirectory.strip()
            load_case_dir = (
                prop.Id
                if not work_item_directory
                else self._extract_path_after(work_item_directory, results_dir)
            )
            work_item_results_subpath = os.path.join(
                results_dir,
                load_case_dir,
            )
            work_item_folder_mapping[prop.Id] = work_item_results_subpath

        return work_item_folder_mapping

    def _validate_workspace(self, workspace):
        if not workspace:
            self._logger.error("Workspace configuration missing or incorrect.")
            return False
        if not workspace.workspace_path:
            self._logger.info(
                "No workspace directory set. Ensure it's set if file upload is required."
            )
            return False
        return True

    def _validate_file_upload_path_inputs(
        self, directory: Optional[str], subdirectory: Optional[str]
    ) -> bool:
        if not directory:
            self._logger.info("No files to upload: No directory specified.")
            return False
        if not os.path.exists(directory):
            self._logger.info(
                "No files to upload: Directory '%s' does not exist.",
                directory,
            )
            return False
        if not subdirectory:
            self._logger.info("No files to upload: No subdirectory specified.")
            return False
        return True

    @staticmethod
    def _get_work_items_id_folder_mapping(
        job_info: Job,
    ) -> dict[str, str]:
        """
        Get a dictionary of work item IDs and their destination folders for the specified Job.

        Args:
            job_info (Job): The Job to get work item information for.

        Returns:
            A dictionary with keys representing work item IDs and values representing the
            destination folders for those work items.
        """
        if not isinstance(job_info.work, (CompositeWork, ParallelWork)):
            return {}
        work_items_id_folder = dict[str, str]()
        work_items = job_info.work.work_items
        for work_item in work_items:
            if not isinstance(work_item, WorkUnit):
                continue
            wi_id = work_item.id
            if (
                not hasattr(work_item, "OutputFileSpecifications")
                or not work_item.output_file_specifications
            ):
                continue
            specs: list[FileTransferSpecification] = (
                work_item.output_file_specifications
            )
            if specs:
                file_spec = specs[0].source_specification
                directory: str = file_spec.directory
                work_items_id_folder[wi_id] = directory
        return work_items_id_folder

    @staticmethod
    def _extract_path_after(path, subpath):
        """Extracts the path after the given subpath.

        Args:
            path: The path to extract the path from.
            subpath: The subpath to look for in the path.

        Returns:
            The path after the subpath, or an empty string if the subpath is not
            found in the path.
        """
        # Split the path into its components.
        path_components = path.split(os.path.sep)

        # Find the index of the subpath in the path components using a list comprehension.
        subpath_indices = [
            i for i, component in enumerate(path_components) if component == subpath
        ]

        # If the subpath is not found in the path, return an empty string.
        if not subpath_indices:
            return ""

        # Get the last occurrence of the subpath.
        subpath_index = subpath_indices[-1]

        # Extract the path after the subpath.
        path_components: list[str] = path_components[subpath_index + 1 :]
        if not path_components:
            return ""

        path_after_subpath = os.path.join(*path_components)

        return path_after_subpath

    def _get_workitem_properties(
        self, job_id: str, work_item_id: Union[str, None] = None
    ) -> Optional[WorkItemProperties]:
        """
        Retrieves the properties of a work item if it exists.

        Args:
            job_id: The job ID.
            work_item_id: The ID of the work item.

        Returns:
            The properties of the work item if it exists; otherwise None.
        """
        if not work_item_id:
            return None

        assert self.onecompute_client is not None
        work_item_properties = self.onecompute_client.get_workitem_properties(
            job_id, work_item_id
        )

        if work_item_properties:
            return work_item_properties[0]
        return None

    def _get_default_storage_uri(self) -> Optional[str]:
        """Returns the default storage URI for the workflow."""
        assert self.onecompute_client is not None
        containers = self.onecompute_client.get_containers()
        if containers is None:
            return None
        container_uri = self.onecompute_client.get_container_uri(containers[0], 1)
        if container_uri is None:
            raise Exception("Error: Failed to retrieve the container URI.")
        return container_uri

    def _get_file_service(
        self, storage_uri: Optional[str] = None
    ) -> Union[FileService, None]:
        """Returns the file service for the workflow."""
        if storage_uri is None:
            storage_uri = self._get_default_storage_uri()
            if storage_uri is None:
                self._logger.error("Failed to retrieve the default storage URI.")
                return None
        callback_func = (
            self.file_transfer_progress_monitor.progress_handler
            if self.file_transfer_progress_monitor
            else None
        )
        if self.cloud_run:
            return AzureBlobStorageFileService(storage_uri, callback_func)
        return HostFileService(storage_uri, callback_func)

    async def _job_status_changed(self, _: OneComputeClient, event: JobEventArgs):
        """Handles job status changed notification"""
        self._logger.info(
            "Job ID: %s. Job Status: %s. Job Progress: %d%%. Job Message: %s",
            event.job_id,
            event.work_status.name,
            int(event.progress * 100),
            event.message,
        )

    async def _job_progress_changed(self, _: OneComputeClient, event: JobEventArgs):
        """Handles job progress changed notification"""
        self._logger.info(
            "Job ID: %s. Job Status: %s. Job Progress: %d%%. Job Message: %s",
            event.job_id,
            event.work_status.name,
            int(event.progress * 100),
            event.message,
        )

    async def _work_item_status_changed(
        self, _: OneComputeClient, event: WorkItemEventArgs
    ):
        """Handles work item status changed notification"""
        self._logger.info(
            "Info: Job ID: %s. Work Item ID: %s. Work Item Status: %s. "
            "Work Item Progress: %d%%. Work Item Message: %s",
            event.job_id,
            event.work_item_id,
            event.work_status.name,
            int(event.progress * 100),
            event.message,
        )

    async def _work_item_progress_changed(
        self, _: OneComputeClient, event: WorkItemEventArgs
    ):
        """Handles work item progress changed notification"""
        self._logger.info(
            "Info: Job ID: %s. Work Item ID: %s. Work Item Status: %s. "
            "Work Item Progress: %d%%. Work Item Message: %s",
            event.job_id,
            event.work_item_id,
            event.work_status.name,
            int(event.progress * 100),
            event.message,
        )


class _LogFileTransferInfo(FileTransferProgressMonitor):
    """This class logs the file transfer info"""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def enable(self):
        """Enables the progress bar."""

    def disable(self):
        """Disables the progress bar."""

    def reset(self):
        """Resets the progress bar."""

    def progress_handler(self, progress_info: ProgressInfo):
        """Handles progress updates."""
        # Don't enclose file info in quotes or other characters to ensure file paths remain
        # navigable in notebooks.
        if progress_info.status == ProgressInfo.Status.QUEUE:
            self._logger.info(
                "Transferring file from %s to %s",
                progress_info.source,
                progress_info.destination,
            )
        elif progress_info.status == ProgressInfo.Status.FAILED:
            self._logger.error(
                "Failed to transfer file from %s to %s",
                progress_info.source,
                progress_info.destination,
            )


@dataclass
class _WorkItemResultStorageInfo:
    """
    Represents storage information for a work item's results.
    """

    job_id: str
    """Gets or sets the ID of the job to which the work item belongs."""

    work_item_name: str
    """Gets or sets the name of the work item."""

    work_item_results_subpath: str
    """Gets or sets the subpath where the work item's results are stored."""

    container_url: str
    """Gets or sets the URL of the container storing the work item's results."""

    is_result_lake: bool
    """
    Gets or sets a flag indicating whether the ResultLake Storage is being utilized for storing
    results.
    """
