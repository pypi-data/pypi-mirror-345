"""
This module defines data classes for configuring OneCompute workflows.
"""

import os
import uuid
from dataclasses import dataclass


@dataclass
class WorkspaceConfiguration:
    """
    A data class that represents the configuration for a workspace.
    """

    workspace_id: str = str(uuid.uuid4())
    """
    Gets or sets the ID of the workspace.
    """

    workspace_path: str = ""
    """
    Gets or sets the path to the workspace directory.
    """

    common_files_directory: str = ""
    """
    Gets or sets the name of the directory where common files are stored.
    """

    load_cases_parent_directory: str = ""
    """
    Gets or sets the name of the parent directory where load cases are stored.
    """

    results_directory: str = ""
    """
    Gets or sets The name of the directory where results are stored.
    """

    @property
    def common_files_fullpath(self) -> str:
        """
        Gets the full path to the directory where common files are stored.
        """
        return os.path.join(self.workspace_path, self.common_files_directory)

    @property
    def results_fullpath(self) -> str:
        """
        Gets the full path to the directory where results are stored.
        """
        return os.path.join(self.workspace_path, self.results_directory)

    @property
    def load_cases_fullpath(self) -> str:
        """
        Gets the full path to the directory where load cases are stored.
        """
        return os.path.join(self.workspace_path, self.load_cases_parent_directory)


@dataclass
class WorkerConfiguration:
    """
    Configuration class for a worker that is used in the OneCompute framework.
    """

    # Temporary until OneCompute accepts this from portal
    command: str = ""
    """
    Gets or sets the command string that is used by the worker.
    """

    service_name: str = ""
    """
    Gets or sets the name of the service used by the worker.
    """

    pool_id: str = ""
    """
    Gets or sets the ID of the pool that the worker should be assigned to.
    """

    use_result_lake_storage: bool = False
    """
    Gets or sets whether the worker should use result lake storage or standard storage.
    """
