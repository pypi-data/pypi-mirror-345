"""This module contains functions for installing the workflow runtime package."""

from ...oneworkflow.package_manager import PackageManager
from ..repository import Repository
from .platform import Platform


async def install_workflow_runtime(
    repository: Repository = Repository.PROD,
    platform: Platform = Platform.WINDOWS,
):
    """
    Asynchronously installs the workflow runtime package.

    This function uses the PackageManager class to install the "LocalWorkflowRuntime" package
    for the specified platform and repository. It is intended for use in setting up the workflow
    runtime environment.

    Args:
        repository (Repository, optional): The repository from which to install the package.
            Default is Repository.PROD.
        platform (Platform, optional): The target platform for the installation. Default is
            Platform.WINDOWS.
    """
    runtime = "linux-x64" if platform == Platform.LINUX else "win-x64"
    await PackageManager().install_package_async(
        "LocalWorkflowRuntime", runtime, repository
    )
