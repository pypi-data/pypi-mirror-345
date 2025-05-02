""" This module contains the FileTransferProgressIndicator class, which is used to monitor and display the progress of file transfers. """

import threading
from typing import Dict, Union

from dnv.onecompute.file_service import ProgressInfo
from tqdm import tqdm as standard_tqdm
from tqdm.notebook import tqdm as notebook_tqdm

from ..file_transfer_progress_monitor import FileTransferProgressMonitor


class FileTransferProgressIndicator(FileTransferProgressMonitor):
    """A class for monitoring and displaying the progress of file transfers."""

    # NOTEBOOK_PROGRESS_BAR_FORMAT: This is the format string for the progress bar used in Jupyter
    # notebooks.
    # It includes the following elements:
    # - {desc:>10}: The description of the progress bar, right-aligned with a width of 10.
    # - {percentage:>3.0f}%: The percentage of progress, right-aligned with a width of 3 and no decimal
    #   places, followed by a percent sign.
    # - |{bar}|: The actual progress bar, enclosed in vertical bars.
    # - {n_fmt}/{total_fmt}: The current progress and total progress.
    # - {postfix}: Any additional information to display at the end of the progress bar.
    NOTEBOOK_PROGRESS_BAR_FORMAT = (
        "{desc:>10} {percentage:>3.0f}% |{bar}| {n_fmt}/{total_fmt} {postfix}"
    )

    # STANDARD_PROGRESS_BAR_FORMAT: This is the format string for the standard progress bar used in console
    # applications.
    # It includes the following elements:
    # - {l_bar}: The left part of the progress bar, which includes the description and the percentage.
    # - {bar:50}: The actual progress bar, with a width of 50.
    # - {r_bar}: The right part of the progress bar, which includes the current progress and total progress.
    # - {bar:-50b}: A binary progress bar, with a width of 50.
    STANDARD_PROGRESS_BAR_FORMAT = "{l_bar}{bar:50}{r_bar}{bar:-50b}"

    def __init__(self):
        super().__init__()
        self._is_enable = False
        self._progress_bars: Dict[str, Union[standard_tqdm, notebook_tqdm]] = {}
        self._position: int = 0
        self._tqdm = standard_tqdm if self._is_standard_python_mode() else notebook_tqdm
        self._bar_format = (
            self.STANDARD_PROGRESS_BAR_FORMAT
            if self._is_standard_python_mode()
            else self.NOTEBOOK_PROGRESS_BAR_FORMAT
        )
        self._lock = threading.Lock()

    def enable(self):
        """Enables the progress bar."""
        self._is_enable = True

    def disable(self):
        """Disables the progress bar."""
        self._is_enable = False

    def reset(self):
        """Reset the progress bars and position."""
        self._progress_bars.clear()
        self._position = 0

    def progress_handler(self, progress_info: ProgressInfo):
        """
        A callback function that is triggered when the progress of a file upload changes.

        Args:
            progress_info (ProgressInfo): The progress information for the file upload.
        """
        if not self._is_enable:
            return

        with self._lock:
            if progress_info.destination not in self._progress_bars:
                progress_bar = self._tqdm(
                    total=progress_info.total,
                    unit="MB",
                    unit_scale=True,
                    position=self._position,
                    leave=True,
                    desc="".ljust(10),
                    bar_format=self._bar_format,
                )
                self._progress_bars[progress_info.destination] = progress_bar
                progress_bar.set_postfix_str(progress_info.destination, refresh=True)
                self._position += 1
            else:
                progress_bar: Union[standard_tqdm, notebook_tqdm] = self._progress_bars[
                    progress_info.destination
                ]

                if (
                    progress_info.current == progress_info.total
                    or progress_info.status == ProgressInfo.Status.IGNORED
                ):
                    progress_bar.update(progress_bar.total)
                    progress_bar.close()
                    return

                progress_bar.update(progress_info.current - progress_bar.n)

    @staticmethod
    def _is_standard_python_mode():
        """
        Checks if the current environment is a standard Python interpreter.

        This function attempts to import the `get_ipython` function from the `IPython` module.
        If the import is successful, it checks if the `get_ipython` function returns a non-None
        value. If it does, it means we're running in a Jupyter Notebook environment. Otherwise,
        we're running in a standard Python interpreter.

        Returns:
            bool: True if the current environment is a standard Python interpreter, False otherwise.
        """
        try:
            from IPython import get_ipython

            return get_ipython() is None
        except ImportError:
            return True
