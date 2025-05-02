"""Module for monitoring and reporting file transfer progress."""

from abc import ABC, abstractmethod

from dnv.onecompute.file_service import ProgressInfo


class FileTransferProgressMonitor(ABC):
    """Abstract base class for a progress bar manager."""

    @abstractmethod
    def enable(self):
        """Enables the progress bar."""

    @abstractmethod
    def disable(self):
        """Disables the progress bar."""

    @abstractmethod
    def reset(self):
        """Resets the progress bar."""

    @abstractmethod
    def progress_handler(self, progress_info: ProgressInfo):
        """Handles progress updates."""
