"""
This module defines the CommandInfo class, which encapsulates command information and related file
operations.
"""

from typing import NamedTuple, Optional

from ...oneworkflow.worker_command import WorkerCommand


class CommandInfo(NamedTuple):
    """
    Encapsulates command information and related file operations.

    This class represents a set of commands to be executed, coupled with information about the
    load case folder and file operations for transferring files between the worker node and blob
    storage.
    """

    commands: list[WorkerCommand]
    """List of WorkerCommand objects specifying the commands to run."""

    load_case_foldername: str
    """Name of the load case folder to be used for the commands."""

    files_to_upload_from_worker_node_to_blob: Optional[list[str]] = ["**/*.*"]
    """
    An optional list of glob patterns that identify the files for copying from the worker node to
    blob storage. For local execution, this process involves copying files from a job folder 
    (serving as the worker node) to a blob folder (serving as blob storage), both within the same
    user-specified temp folder. For cloud execution, it involves uploading files directly from the
    worker node to cloud blob storage. This attribute facilitates selective file upload to blob 
    storage post command execution. If not specified, all files from the worker node will be
    uploaded.
    """

    files_to_download_from_blob_to_worker_node: Optional[list[str]] = ["**/*.*"]
    """
    An optional list of glob patterns that specify the files for downloading from blob storage to
    the worker node. For local execution, this process involves copying files from a blob folder
    (serving as blob storage) to a job folder (serving as the worker node), both within the same
    user-specified temp folder. For cloud execution, it involves downloading files directly from
    cloud blob storage to the worker node. This attribute facilitates selective file download from
    blob storage prior to command execution. If not specified, all files in the blob storage will be
    downloaded.
    """
