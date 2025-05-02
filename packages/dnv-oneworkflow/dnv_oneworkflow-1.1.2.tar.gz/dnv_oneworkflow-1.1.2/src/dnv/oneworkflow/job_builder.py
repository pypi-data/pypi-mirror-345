"""
The module features the JobBuilder class, which is responsible for generating job definitions based
on workspace configurations, streamlining the process of building jobs.
"""

import os
from typing import Any, Dict, Generator, List, Optional, Union

from dnv.onecompute.file_specification import FileSpecification
from dnv.onecompute.flowmodel import (
    BlobDirectorySpecification,
    FileSelectionOptions,
    FileSystemDirectorySpecification,
    FileTransferSpecification,
    Job,
    ParallelWork,
    ResultLakeStorageSpecification,
    SchedulingOptions,
    StorageSpecification,
    WorkItem,
    WorkUnit,
)
from dnv.onecompute.one_compute_client import OneComputeClient
from dnv.oneworkflow.composite_executable_command import CompositeExecutableCommand
from dnv.oneworkflow.config import WorkerConfiguration, WorkspaceConfiguration
from dnv.oneworkflow.worker_command import WorkerCommand

from .container_execution_workunit import ContainerSettingsNames


class JobBuilder:
    """
    A utility class to build and submit jobs to OneCompute.
    """

    _INPLACE_EXECUTION_DIR = (
        "."  # The current working directory for in-place execution.
    )

    def __init__(
        self,
        onecompute_client: OneComputeClient,
        workspace_config: WorkspaceConfiguration,
        worker_config: WorkerConfiguration,
        cloud_run: bool,
        inplace_execution: bool,
    ):
        """
        Initializes a new instance of the JobBuilder class.

        Args:
            onecompute_client (OneComputeClient): A OneCompute client instance used to communicate
                with the OneCompute service.
            workspace_config (WorkspaceConfiguration): The workspace configuration.
            worker_config (WorkerConfiguration): The worker configuration.
            cloud_run (bool): Flag indicating whether the execution context is cloud-based or not.
            inplace_execution (bool): Flag indicating whether the execution is in-place or not.
        """
        self._worker_config = worker_config
        self._onecompute_client = onecompute_client
        self._workspace = workspace_config
        self._cloud_run = cloud_run
        self._use_result_lake = worker_config.use_result_lake_storage
        self._inplace_execution = inplace_execution

    def create_job(
        self,
        work: ParallelWork | WorkUnit | WorkItem,
        job_preparation_work: Optional[WorkUnit] = None,
        job_release_work: Optional[WorkUnit] = None,
        scheduling_options: Optional[SchedulingOptions] = None,
        time_out: str = "",
    ) -> Job:
        """
        Creates a new OneCompute job.

        Args:
            work (ParallelWork | WorkUnit | WorkItem): The main work to be processed in the
                workflow.
            job_preparation_work (Optional[WorkUnit]): An optional work unit representing the
                preparation steps before the main work item is processed.
            job_release_work (Optional[WorkUnit]): An optional work unit representing the
                post-processing steps after the main work item is processed.
            scheduling_options (SchedulingOptions): The scheduling options for the job.
            time_out (str, optional): The timeout value for the job. Defaults to "".

        Returns:
            Job: The newly created job.

        Raises:
            ValueError: Failed to create job. The web API did not return any containers.
            ValueError: Failed to create job. The web API did not return container URI.
        """

        # TODO: Validate functionality across all 'work' types which are derivatives and variants
        # of WorkItem.

        containers = self._onecompute_client.get_containers()
        if not containers:
            raise ValueError(
                "Failed to create job. The web API did not return any containers."
            )

        container_uri = self._onecompute_client.get_container_uri(containers[0], 1)
        if not container_uri:
            raise ValueError(
                "Failed to create job. The web API did not return container URI."
            )

        common_files_rel_path = self._workspace.common_files_directory

        # Update the FileTransferSpecifications
        reduction_work_item: Optional[WorkItem] = None
        work_items: List[WorkItem] = []

        if isinstance(work, ParallelWork):
            work_items = work.work_items
            if work.reduction_task:
                reduction_work_item = work.reduction_task
                if isinstance(reduction_work_item, WorkUnit):
                    self._update_work_unit(
                        reduction_work_item, container_uri, common_files_rel_path
                    )
        elif isinstance(work, WorkUnit):
            work_items = [work]

        for it_work_item in work_items:
            if isinstance(it_work_item, WorkUnit):
                self._update_work_unit(
                    it_work_item, container_uri, common_files_rel_path
                )

        job = Job()
        if self._inplace_execution:
            job.properties["OC_SHARED_FOLDER"] = self._workspace.workspace_path
        else:
            job.properties["OW_WorkspaceId"] = self._workspace.workspace_id

        job.SchedulingOptions = scheduling_options
        job.service_name = self._worker_config.service_name
        job.pool_id = (
            self._worker_config.pool_id if self._worker_config.service_name else None
        )

        # For containerized work, don't create default job preparation and release tasks,
        # because these won't work on a containerized WorkerHost.
        # Use the provided job_preparation_work and job_release_work values if supplied.
        # If any of the work units have an image name set, the we assume this is a containerized
        # job.
        if any(ContainerSettingsNames.IMAGE_NAME in wi.properties for wi in work_items):
            job.job_preparation_work = job_preparation_work
            job.job_release_work = job_release_work
        # For in-place execution, there is no need to generate the job preparation and release
        # work, as the work will be executed on the same workspace folder where the input files
        # are located.
        elif not self._inplace_execution:
            job.job_preparation_work = self._build_job_preparation_work(
                job_preparation_work, container_uri
            )
            job.job_release_work = self._build_job_release_work(
                job_release_work, container_uri
            )

        job.work = work
        job.timeout_seconds = time_out.strip() if time_out.strip() else None
        return job

    def _build_job_preparation_work(
        self, job_preparation_work: Optional[WorkUnit], container_uri: str
    ):
        common_files_fullpath = self._workspace.common_files_fullpath
        common_files_rel_path = self._workspace.common_files_directory
        work_unit = job_preparation_work if job_preparation_work else WorkUnit()

        # Check if the common-files folder is present and has input files, and if so,
        # set the common_files_input_spec_needed flag to True for use in the job-preparation task.
        common_files_input_spec_needed = (
            common_files_rel_path
            and os.path.exists(common_files_fullpath)
            and any(os.listdir(common_files_fullpath))
        )

        # Check if the work unit contains the input-files selector for the common-files folder
        wu_ifs = work_unit.input_file_selectors
        common_files_selector = [
            sel for sel in wu_ifs if sel.directory == common_files_rel_path
        ]

        if common_files_selector:
            # Assuming the user added the common-files folder only once
            if "**/*.*" not in common_files_selector[0].include_files:
                common_files_selector[0].include_files.append("**/*.*")
        elif common_files_input_spec_needed:
            # Add the input-files selector for the common-files folder
            work_unit.input_file_selectors.append(
                FileSelectionOptions(common_files_rel_path, ["**/*.*"], [])
            )

        self._update_work_unit(
            work_unit=work_unit,
            container_uri=container_uri,
            common_files_rel_path=common_files_rel_path,
        )

        return work_unit

    def _build_job_release_work(
        self, job_release_work: Optional[WorkUnit], container_uri: str
    ):
        """
        Update the job release work unit with the container URI and common files relative path.

        This method updates the job release work unit with the provided container URI and the
        common files relative path from the workspace. If the job release work unit is None,
        no update is performed and None is returned.

        Args:
            job_release_work (Optional[WorkUnit]): The job release work unit to update. If None,
                no update is performed.
            container_uri (str): The container URI to set in the job release work unit.

        Returns:
            Optional[WorkUnit]: The updated job release work unit, or None if no update was
            performed.
        """
        common_files_rel_path = self._workspace.common_files_directory
        if job_release_work:
            self._update_work_unit(
                work_unit=job_release_work,
                container_uri=container_uri,
                common_files_rel_path=common_files_rel_path,
            )
        return job_release_work

    def _update_work_unit(
        self, work_unit: WorkUnit, container_uri: str, common_files_rel_path: str
    ):
        work_unit.command = self._worker_config.command
        work_unit.working_directory = None

        if self._inplace_execution:
            self._update_working_directory(work_unit, self._INPLACE_EXECUTION_DIR)
        else:
            self._prepare_input_output_file_transfer_specs(work_unit)
            self._update_input_output_file_transfer_specs_container_uri(
                work_unit, container_uri
            )
        self._update_file_specification(work_unit, common_files_rel_path)

    def _update_input_output_file_transfer_specs_container_uri(
        self, work_unit: WorkUnit, container_uri: str
    ):
        """
        Update the container URI of the specified WorkUnit.

        Args:
            work_unit (WorkUnit): The WorkUnit to update.
            container_uri (str): The new container URI to use for the WorkUnit.
        """
        for file_specs in [
            work_unit.input_file_specifications,
            work_unit.output_file_specifications,
        ]:
            for spec in file_specs:
                self._update_file_transfer_spec_container_uri_directory(
                    spec, container_uri
                )

    def _prepare_input_output_file_transfer_specs(self, work_unit: WorkUnit):
        """
        Prepare input and output file transfer specifications for the specified WorkUnit.

        Args:
            work_unit (WorkUnit): The WorkUnit for which to prepare the specifications.
        """
        work_unit.input_file_specifications = self._prepare_input_file_specifications(
            work_unit
        )
        work_unit.output_file_specifications = self._prepare_output_file_specifications(
            work_unit
        )

    def _prepare_input_file_specifications(
        self, work_unit: WorkUnit
    ) -> List[FileTransferSpecification]:
        """
        Prepare the input file specifications for a given work unit.

        Args:
            work_unit (WorkUnit): The work unit for which to prepare the input file specifications.

        Returns:
            List[FileTransferSpecification]: The list of prepared file transfer specifications.
        """
        workspace_id = self._workspace.workspace_id
        input_file_specifications = list[FileTransferSpecification]()
        for ifs in work_unit.input_file_selectors:
            src_dir = os.path.join(workspace_id, ifs.directory)
            dstn_dir = ifs.directory
            include_files = ifs.include_files
            exclude_files = ifs.exclude_files
            src_spec = BlobDirectorySpecification()
            dstn_spec = FileSystemDirectorySpecification()
            input_file_specifications.append(
                self._create_file_transfer_specification(
                    src_dir, dstn_dir, include_files, exclude_files, src_spec, dstn_spec
                )
            )
        return input_file_specifications

    def _prepare_output_file_specifications(
        self, work_unit: WorkUnit
    ) -> List[FileTransferSpecification]:
        """
        Prepares output file transfer specifications for a work unit.

        Args:
            work_unit (WorkUnit): The work unit to prepare specifications for.

        Returns:
            List[FileTransferSpecification]: The prepared output file transfer specifications.
        """
        workspace_id = self._workspace.workspace_id
        output_file_specifications = list[FileTransferSpecification]()
        for ofs in work_unit.output_file_selectors:
            src_dir = ofs.directory
            dstn_dir = os.path.join(workspace_id, ofs.directory)
            include_files = ofs.include_files
            exclude_files = ofs.exclude_files
            src_spec = FileSystemDirectorySpecification()
            dstn_spec = (
                ResultLakeStorageSpecification()
                if self._use_result_lake and self._cloud_run
                else BlobDirectorySpecification()
            )
            output_file_specifications.append(
                self._create_file_transfer_specification(
                    src_dir,
                    dstn_dir,
                    include_files,
                    exclude_files,
                    src_spec,
                    dstn_spec,
                )
            )
        return output_file_specifications

    @staticmethod
    def _update_file_transfer_spec_container_uri_directory(
        spec: FileTransferSpecification, container_uri: str
    ):
        """
        Update the container URI and directory of a FileTransferSpecification.

        Args:
            spec (FileTransferSpecification): The FileTransferSpecification to update.
            container_uri (str): The new container URI to use for the FileTransferSpecification.
        """
        for spec_type in [spec.SourceSpecification, spec.DestinationSpecification]:
            if isinstance(spec_type, BlobDirectorySpecification):
                if not spec_type.container_url.strip():
                    spec_type.container_url = container_uri
            elif isinstance(spec_type, FileSystemDirectorySpecification):
                if not spec_type.directory.strip():
                    spec_type.directory = container_uri

    @staticmethod
    def _create_file_transfer_specification(
        src_dir: str,
        dstn_dir: str,
        include_files: List[str],
        exclude_files: List[str],
        src_spec: StorageSpecification,
        dstn_spec: StorageSpecification,
    ) -> FileTransferSpecification:
        """
        Creates a file transfer specification.

        Args:
            src_dir (str): The source directory.
            dstn_dir (str): The destination directory.
            include_files (List[str]): The files to include in the transfer.
            exclude_files (List[str]): The files to exclude from the transfer.
            src_spec (StorageSpecification): The source storage specification.
            dstn_spec (StorageSpecification): The destination storage specification.

        Returns:
            FileTransferSpecification: The created file transfer specification.
        """
        spec = FileTransferSpecification()
        spec.selected_files = include_files
        spec.excluded_files = exclude_files or []
        spec.source_specification = src_spec
        spec.source_specification.directory = src_dir  # type: ignore
        spec.destination_specification = dstn_spec
        spec.destination_specification.directory = dstn_dir  # type: ignore
        return spec

    def _update_file_specification(
        self, work_unit: WorkUnit, common_files_rel_path: str
    ):
        """
        Updates the file specifications within a work unit's content.

        This method checks if the content of a work unit is an instance of WorkerCommand. If
        it is, it finds instances of FileSpecification in the content's attributes and updates
        their attributes using the _update_file_specification_instance method.

        Args:
            work_unit (WorkUnit): The work unit containing the content to be updated.
            common_files_rel_path (str): The common files relative path.

        Returns:
            None
        """
        if not isinstance(work_unit.data.content, WorkerCommand):
            return

        wu_working_directory = work_unit.working_directory
        content = work_unit.data.content

        for file_spec in JobBuilder._get_file_specification_instance(vars(content)):
            self._update_file_specification_instance(
                [file_spec],
                common_files_rel_path,
                content.working_directory,
                wu_working_directory,
            )

    @staticmethod
    def _update_working_directory(work_unit: WorkUnit, working_directory: str):
        """
        This function updates the working directory of a work unit and its content.

        The working directory of the work unit is set to the directory obtained from the work
        item content. If the content is a WorkerCommand, its working directory is updated. If
        the content is also a CompositeExecutableCommand, the working directory is updated for
        each of its executable commands.

        Args:
            work_unit (WorkUnit): The work unit for which to update the working directory.
            working_directory (str): The working directory to set.

        Returns:
            None
        """
        work_unit.working_directory = (
            JobBuilder._get_work_item_content_working_directory(work_unit)
        )

        content = work_unit.data.content
        if isinstance(content, WorkerCommand):
            content.working_directory = working_directory
            if isinstance(content, CompositeExecutableCommand):
                for cmd in content.executable_commands:
                    cmd.working_directory = working_directory

    @staticmethod
    def _get_work_item_content_working_directory(work_unit: WorkUnit) -> str:
        """
        This function retrieves the working directory from the content of a work unit.

        If the content is a WorkerCommand, it returns its working directory. If the content is a
        CompositeExecutableCommand(which is a subclass of WorkerCommand) and no working directory
        has been specified for the CompositeExecutableCommand, it iterates over the executable
        commands and returns the working directory of the first command that has a non-empty
        working directory. If no working directory is found, it returns an empty string.

        Args:
            work_unit (WorkUnit): The work unit from which to retrieve the working directory.

        Returns:
            str: The working directory of the content of the work unit, or an empty string if no
            working directory is found.
        """
        content = work_unit.data.content

        if not isinstance(content, WorkerCommand):
            return ""

        wd = content.working_directory.strip()

        if wd or not isinstance(content, CompositeExecutableCommand):
            return wd

        for cmd in content.executable_commands:
            cmd_wd = cmd.working_directory.strip()
            if cmd_wd:
                return cmd_wd

        return ""

    @staticmethod
    def _get_file_specification_instance(
        d: Dict[str, Union[Any, List[Any]]]
    ) -> Generator[FileSpecification, None, None]:
        """
        Recursively search a dictionary for instances of FileSpecification.

        This method traverses a dictionary, which can contain other dictionaries and lists as
        values, to find all instances of FileSpecification. It returns a generator that yields
        each FileSpecification instance it finds.

        Args:
            d (Dict[str, Union[Any, List[Any]]]): The dictionary to search.

        Returns:
            Generator[FileSpecification, None, None]: A generator that yields each
            FileSpecification instance found in the dictionary.
        """
        for v in d.values():
            if isinstance(v, FileSpecification):
                yield v
            elif isinstance(v, dict):
                yield from JobBuilder._get_file_specification_instance(v)
            elif isinstance(v, list):
                for item in v:
                    yield from JobBuilder._process_list_item(item)

    @staticmethod
    def _process_list_item(item: Any) -> Generator[FileSpecification, None, None]:
        """
        Process a list item to find instances of FileSpecification.

        This method checks the type of the item and processes it accordingly to find instances of
        FileSpecification. If the item is a basic data type, it is ignored. If the item is a
        dictionary or a list, it is recursively processed. If the item is an object, its
        attributes are processed.

        Args:
            item (Any): The item to process.

        Returns:
            Generator[FileSpecification, None, None]: A generator that yields each
            FileSpecification instance found in the item.
        """
        if isinstance(
            item,
            (str, int, float, complex, bool, bytes, bytearray, memoryview),
        ):
            return
        if isinstance(item, dict):
            yield from JobBuilder._get_file_specification_instance(item)
        elif isinstance(item, list):
            yield from JobBuilder._get_file_specification_instance({"_": item})
        else:
            yield from JobBuilder._get_file_specification_instance(vars(item))

    @staticmethod
    def _get_file_specification_attrs(
        command: WorkerCommand,
    ) -> List[tuple[str, FileSpecification]]:
        """
        Retrieves attributes of a WorkerCommand that are FileSpecification instances.

        Parameters:
        command (WorkerCommand): The command from which to retrieve attributes.

        Returns:
            list[tuple[str, FileSpecification]]: List of tuples with attribute name and its
            FileSpecification instance.
        """
        return [
            (name, getattr(command, name))
            for name in dir(command)
            if isinstance(getattr(command, name), FileSpecification)
        ]

    @staticmethod
    def _update_file_specification_instance(
        file_spec_attrs: List[FileSpecification],
        common_files_rel_path: str,
        worker_command_working_directory: str,
        work_unit_working_directory: Optional[str],
    ):
        """
        Modifies a list of file specifications by adjusting their 'directory' and 'sharedfolder'
        attributes.

        Each file specification's 'sharedfolder' attribute is determined by whether its
        directory begins with the specified common files relative path. When inplace execution is
        enabled and a directory is specified for the file, the function verifies if this directory
        is a subdirectory of the work unit's directory. If it is, the 'directory' attribute of the
        file specification is updated to reflect its relative path from the work unit's directory.
        The 'directory' attribute is further adjusted based on the existence of a filename: if a
        filename is present, the directory retains its current value or defaults to the worker
        command's working directory if undefined.

        Args:
            file_spec_attrs (List[FileSpecification]): The file specifications to be modified.
            common_files_rel_path (str): The relative path to the common files.
            worker_command_working_directory (str): The working directory of the worker command.
            work_unit_working_directory (Optional[str]): The working directory of the work unit.

        Returns:
            None
        """
        for value in file_spec_attrs:
            if os.path.isabs(value.directory):
                continue

            value.sharedfolder = bool(value.directory.startswith(common_files_rel_path))

            if work_unit_working_directory and value.directory:
                common_path = os.path.commonpath(
                    [work_unit_working_directory, value.directory]
                )
                if common_path == work_unit_working_directory:
                    value.directory = os.path.relpath(
                        value.directory, work_unit_working_directory
                    )

            if value.filename.strip():
                value.directory = (
                    value.directory
                    if value.directory
                    else worker_command_working_directory
                )
