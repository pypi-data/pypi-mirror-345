"""
This module defines the ContainerExecutionWorkUnit. This is a WorkUnit which is runs a containerised
task, either in Azure Batch or in the OneCompute Kubernetes backend.

There are also two data classes, KubernetesPropertyNames and ContainerSettingsNames, for managing
property names and settings related to Kubernetes and containers, respectively. These classes are
marked as frozen for immutability.
"""

from dataclasses import dataclass
from typing import Optional

from dnv.onecompute.flowmodel import WorkUnit


@dataclass(frozen=True)
class KubernetesPropertyNames:
    """
    A class that defines constants for Kubernetes property names.
    """

    CPU_REQUEST: str = "CpuRequest"
    """
    Gets the name of the CPU request property.
    """

    CPU_LIMIT: str = "CpuLimit"
    """
    Gets the name of the CPU limit property.
    """

    MEMORY_REQUEST: str = "MemoryRequest"
    """
    Gets the name of the memory request property.
    """

    MEMORY_LIMIT: str = "MemoryLimit"
    """
    Gets the name of the memory limit property.
    """

    TOLERATIONS: str = "Tolerations"
    """
    Gets the names of the toleration properties.
    """


@dataclass(frozen=True)
class ContainerSettingsNames:
    """
    Defines names of custom properties for containerized WorkItem execution.
    """

    IMAGE_NAME: str = "ImageName"
    """
    Gets the name of property used to indicate the image that will be used to execute a WorkUnit
    """

    RUN_OPTIONS: str = "RunOptions"
    """
    Gets the name of property used to indicate the run options for launching acontainer to execute
    a WorkUnit.
    """


class ContainerExecutionWorkUnit(WorkUnit):
    """
    A class that represents a work unit that executes in a container.

    Attributes:
        properties (dict): A dictionary to hold the properties of the container execution work unit.
    """

    def __init__(
        self,
        json_string: str,
        image_registry: str,
        image_repository: str,
        image_tag: str,
        work_unit_id: str = "",
        cpu_request: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        memory_request: Optional[str] = None,
        memory_limit: Optional[str] = None,
        tolerations: Optional[str] = None,
    ):
        """
        Initializes a new instance of the ContainerExecutionCommand class.

        Args:
            json_string (str): The JSON input for the work unit.
            image_registry (str): The registry containing the image (e.g. onecompute.azurecr.io).
            image_repository (str): The name of the image.
            image_tag (str): The image tag.
            work_unit_id (str): An ID for the work unit. Defaults to an empty string.
            cpu_request (Optional[str]): The requested CPU resources.
            cpu_limit (Optional[str]): The maximum CPU resources.
            memory_request (Optional[str]): The requested memory resources.
            memory_limit (Optional[str]): The maximum memory resources.
            tolerations (Optional[str]): A semi-colon delimited list of tolerations.

        Note: The CPU and memory requests and limits, and the tolerations are only relevant
        when the container runs in the OneCompute Kubernetes backend. They will be ignored
        if running in Azure Batch.
        """
        super().__init__(data=json_string, work_unit_id=work_unit_id)
        image_name = f"{image_registry}/{image_repository}:{image_tag}"
        self.properties[ContainerSettingsNames.IMAGE_NAME] = image_name
        self.properties[KubernetesPropertyNames.CPU_REQUEST] = cpu_request
        self.properties[KubernetesPropertyNames.CPU_LIMIT] = cpu_limit
        self.properties[KubernetesPropertyNames.MEMORY_REQUEST] = memory_request
        self.properties[KubernetesPropertyNames.MEMORY_LIMIT] = memory_limit
        self.properties[KubernetesPropertyNames.TOLERATIONS] = tolerations
