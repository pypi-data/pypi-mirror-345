""" This module provides a class for managing and controlling processes by name. """

import logging
from typing import List, Optional

import psutil


class ProcessManager:
    """
    A class that provides functionality for managing and controlling processes by name.

    This class includes methods for finding, terminating, and retrieving information about
    processes. It is initialized with the name of the process to manage, and all operations
    are performed on processes with this name.

    Attributes:
        process_name (str): The name of the process to manage.
    """

    def __init__(self, process_name: str):
        """
        Constructs an instance of ProcessManager object.

        Args:
            process_name (str): The name of the process to manage.
        """
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.process_name = process_name

    def find_process_by_name(self) -> Optional[psutil.Process]:
        """
        Finds and returns the first process with the given name.

        Returns:
            Optional[psutil.Process]: The first process with the given name, or None if no such
            process is found.
        """
        processes = self._get_processes_by_name()

        if not processes:
            logging.info("No process found with the name '%s'.", self.process_name)
            return None

        # Return the first process found with the given name
        return processes[0]

    def find_processes_by_name(self) -> Optional[List[psutil.Process]]:
        """
        Finds and returns all processes with the given name.

        Returns:
            Optional[List[psutil.Process]]: A list of processes with the given name, or an empty
            list if no such processes are found.
        """
        processes = self._get_processes_by_name()

        if not processes:
            logging.info("No processes found with the name '%s'.", self.process_name)
            return []

        # Return the list of processes found with the given name
        return processes

    def terminate_process(self, force: bool = False):
        """
        Terminates the process with the given name.

        Args:
            force (bool, optional): Whether to forcefully terminate the process and its descendants.
                Defaults to False.
        """
        process = self.find_process_by_name()
        if not process:
            return

        try:
            if force:
                # Forcefully terminate the process and its descendants
                self.terminate_process_tree(process.pid)
            else:
                self._terminate_process(process.pid, process.name(), process)
        except Exception as e:
            self._log_process_termination_error(process, e)

    def terminate_processes(self, force=False):
        """
        Terminates all processes with the given name.

        If the `force` parameter is True, it forcefully terminates each process and its descendants.
        If the `force` parameter is False, it requests termination of each process.

        Args:
            force (bool, optional): Whether to forcefully terminate each process and its
                descendants. Defaults to False.
        """
        processes = self.find_processes_by_name()
        if not processes:
            return

        # Terminate each matching process
        for process in processes:
            try:
                if force:
                    # Forcefully terminate the process and its descendants
                    self.terminate_process_tree(process.pid)
                else:
                    self._terminate_process(process.pid, process.name(), process)
            except Exception as e:
                self._log_process_termination_error(process, e)

    def terminate_process_tree(self, pid: int):
        """
        Terminates a process and its descendants.

        Args:
            pid (int): The process ID of the parent process.
        """
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # Include the parent process
        processes = [(p.pid, p.name(), p) for p in children + [parent]]

        # Terminate each process in the process tree
        for pid, pname, process in processes:
            self._terminate_process(pid, pname, process)

    def _get_processes_by_name(self):
        """
        Retrieves all processes with the name specified in the `process_name` attribute.

        This method performs a case-insensitive search for all processes with the given name.
        If an error occurs during the search, it prints the error message and returns an empty list.

        Returns:
            list: A list of processes with the given name, or an empty list if no such processes are
            found or an error occurs.
        """
        process_name = self.process_name.casefold()
        try:
            # Get a list of all processes with the given name (case-insensitive)
            processes = [
                p
                for p in psutil.process_iter(["pid", "name"])
                if p.name().casefold() == process_name
            ]
            return processes
        except Exception as e:
            logging.error("%s", e)
            return []

    @staticmethod
    def _terminate_process(pid: int, pname: str, process: psutil.Process):
        """
        Terminates a given process and logs the termination.

        Args:
            pid (int): The PID of the process to terminate.
            pname (str): The name of the process to terminate.
            process (psutil.Process): The process to terminate.
        """
        try:
            process.terminate()
            process.wait()
            ProcessManager._log_process_termination(pid, pname)
        except psutil.NoSuchProcess:
            # The process has already terminated
            ProcessManager._log_process_termination(pid, pname)

    @staticmethod
    def _log_process_termination(pid: int, pname: str):
        """
        Log the termination of a process.

        Args:
            pid (int): The PID of the process that has been terminated.
            pname (str): The name of the process that has been terminated.
        """
        logging.info(
            "Process '%s' with PID %s has been successfully terminated.",
            pname,
            pid,
        )

    @staticmethod
    def _log_process_termination_error(process: psutil.Process, error: Exception):
        """
        Log an error that occurred while terminating a process.

        Args:
            process (psutil.Process): The process that was being terminated.
            error (Exception): The error that occurred.
        """
        logging.error(
            "An error occurred while terminating process '%s' with PID %s: %s",
            process.name(),
            process.pid,
            error,
        )
