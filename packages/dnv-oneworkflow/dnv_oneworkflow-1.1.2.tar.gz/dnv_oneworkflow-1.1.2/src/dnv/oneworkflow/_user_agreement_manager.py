"""This module contains the UserAgreementManager class."""

import getpass
import hashlib
import json
import os
import uuid
from datetime import datetime
from logging import WARNING, Logger, getLogger
from tkinter import BOTH, END, YES, Button, Text, Tk, messagebox
from typing import Optional, Union

import httpx

from .logging_utils import set_log_level, setup_logger
from .repository import Repository


class UserAgreementManager:
    """
    This class handles the user agreement process for a software application.

    It retrieves the terms and conditions from a specified source, determines if they have been
    updated since the last user acceptance, and provides methods for the user to accept or reject
    the updated terms and conditions.
    """

    OW_TERMS_ACCEPTANCE_DETAILS_FILE = ".ow_terms_acceptance_details_file"
    """
    The name of the file where the details of the user's acceptance of the terms and conditions are
    stored. This includes the date of acceptance, machine ID, agreement status, and the SHA version
    of the terms. This file is located in the user's home directory.
    """

    def __init__(self, repository: Repository, logger: Optional[Logger] = None):
        """
        Initializes a new instance of the UserAgreementManager class. This class manages the terms
        and conditions fetched from a specified repository and logs messages during its operations
        using the provided logger.

        Args:
            repository (Repository): The repository from which to fetch the terms and conditions.
                This can be one of the values from the Repository enum, i.e., DEV, TEST, or PROD.
            logger (Optional[Logger]): The logger to use for logging any messages or errors
                encountered during the fetching and processing of the terms and conditions.
                Default to None, which means that a new logger will be created with the name of
                this class with the logging level set to INFO.
        """
        # The repository from which to fetch the terms and conditions.
        self._repository: Repository = repository

        # The logger to use for logging messages.
        self._logger = setup_logger(self.__class__.__name__, logger)

        # Stores the terms and conditions text fetched from the internet. This is initially set to
        # None, and the terms and conditions are fetched and stored in this variable when they are
        # first accessed. This prevents multiple internet fetches.
        self._terms_conditions: Optional[str] = None

        # The path to the file where the agreement information is stored.
        self._agreement_file_path: str = UserAgreementManager.agreement_file_path()

        # The SHA256 hash of the last accepted version of the terms and conditions.
        self._last_accepted_sha_version: Union[str, None] = (
            self._get_last_accepted_sha_version()
        )

        # The Tkinter window for displaying the terms and conditions.
        self._window: Optional[Tk] = None

        # Indicates whether the user accepted the terms and conditions. Default to True, which means
        # that the user accepted the terms and conditions.
        self._user_accepted: bool = True

    def show(self) -> bool:
        """
        Display the terms and conditions to the user in a new window. If the terms and conditions
        have changed since the last acceptance, this method creates a new Tkinter window, fetches
        the current terms and conditions, and displays them in the window. The window also includes
        "I Accept" and "I Reject" buttons for the user to accept or reject the terms and conditions.

        Returns:
            bool: True if the user accepted the terms and conditions, False otherwise.
        """
        if self._check_if_changed():
            # Show the terms and conditions to the user
            self._window = Tk()
            self._window.attributes(
                "-topmost", 1
            )  # This line makes the window appear on top
            text = Text(self._window)
            text.insert(END, self._get_terms_conditions())
            text.pack(
                expand=YES, fill=BOTH
            )  # This line makes the text widget expand and fill the window
            accept_button = Button(self._window, text="I Accept", command=self._accept)
            reject_button = Button(self._window, text="I Reject", command=self._reject)
            accept_button.pack()
            reject_button.pack()
            self._window.mainloop()
        else:
            self._logger.info(
                "No changes in terms and conditions since last acceptance."
            )
        return self._user_accepted

    @staticmethod
    def agreement_file_path() -> str:
        """Return the path to the terms and conditions acceptance file."""
        return os.path.join(
            os.path.expanduser("~"),
            UserAgreementManager.OW_TERMS_ACCEPTANCE_DETAILS_FILE,
        )

    @set_log_level(getLogger("httpx"), WARNING)
    def _get_terms_conditions(self) -> str:
        """
        Fetches and returns the terms and conditions. If already fetched, returns the cached
        version. In case of a fetch error, logs the error and raises an exception.

        Returns:
            str: The terms and conditions text.

        Raises:
            Exception: If fetching the terms and conditions fails.
        """
        if self._terms_conditions is None:
            self._logger.info("Fetching the terms and conditions.")
            url = self._get_terms_conditions_url()
            try:
                response = httpx.get(url)
                response.raise_for_status()
            except httpx.HTTPStatusError as err:
                self._logger.error(
                    "Failed to fetch terms and conditions due to HTTP error '%s'",
                    err.response.reason_phrase,
                )
                raise Exception("Could not download the terms and conditions.")
            except Exception as err:
                self._logger.error("An error occurred: %s", err)
                raise Exception("Could not download the terms and conditions.")
            self._terms_conditions = response.text
            self._logger.info("Downloaded the terms and conditions.")
        return self._terms_conditions

    def _get_last_accepted_sha_version(self) -> Union[str, None]:
        """
        Retrieve the SHA version of the last accepted terms and conditions.

        Returns:
            str, None: The SHA version of the last accepted terms and conditions, or None if
            the agreement file does not exist.
        """
        if os.path.exists(self._agreement_file_path):
            with open(self._agreement_file_path, "r", encoding="utf-8") as file:
                agreement_info = json.load(file)
                return agreement_info.get("sha_version")
        return None

    def _get_terms_conditions_url(self):
        """
        Generate the URL to fetch the terms and conditions from the specified repository.

        Returns:
            str: The URL to fetch the terms and conditions.
        """
        terms_conditions_url: str = (
            "https://{storage_account}.blob.core.windows.net/terms-and-conditions/content.txt"
        )
        return terms_conditions_url.format(storage_account=self._repository.value)

    def _hash_terms_conditions(self, terms_conditions: str) -> str:
        """
        Compute the SHA256 hash of the given terms and conditions.

        This method takes a string of terms and conditions, encodes it to bytes, and then computes
        the SHA256 hash of the byte string. The hash is returned as a hexadecimal string.

        Args:
            terms_conditions (str): The terms and conditions to hash.

        Returns:
            str: The SHA256 hash of the terms and conditions, as a hexadecimal string.
        """
        return hashlib.sha256(terms_conditions.encode()).hexdigest()

    def _check_if_changed(self) -> bool:
        """
        Check if the terms and conditions have changed since the last acceptance.

        This method fetches the current terms and conditions, computes their SHA256 hash, and
        compares it to the SHA256 hash of the last accepted terms and conditions. If the hashes
        are different, it means the terms and conditions have changed.

        Returns:
            bool: True if the terms and conditions have changed, False otherwise.
        """
        current_terms_conditions = self._get_terms_conditions()
        if current_terms_conditions is None:
            return False
        current_sha_version = self._hash_terms_conditions(current_terms_conditions)
        return current_sha_version != self._last_accepted_sha_version

    def _capture_signature(self) -> str:
        """
        Captures the user's digital signature.

        Returns:
            str: The user's digital signature.
        """
        username = getpass.getuser()
        signature_hash = hashlib.sha256(username.encode()).hexdigest()
        return signature_hash

    def _accept(self) -> None:
        """
        Handle the acceptance of the terms and conditions.

        This method is called when the user clicks the "I Accept" button. It fetches the current
        terms and conditions, computes their SHA256 hash, and stores this hash along with the
        current date and time in the agreement file. This information is used to check if the
        terms and conditions have changed since the last acceptance.
        """
        current_terms_conditions = self._get_terms_conditions()
        current_sha_version = self._hash_terms_conditions(current_terms_conditions)
        user_acceptance_details = {
            "date": datetime.now().isoformat(),
            "machine_id": uuid.getnode(),
            "agreement": "yes",
            "sha_version": current_sha_version,
            "user_signature": self._capture_signature(),
        }
        with open(self._agreement_file_path, "w", encoding="utf-8") as file:
            json.dump(user_acceptance_details, file)
        self._last_accepted_sha_version = current_sha_version
        messagebox.showinfo("Info", "You have accepted the terms and conditions.")
        self._logger.info("User has accepted the terms and conditions.")
        if self._window is not None:
            self._window.destroy()
        self._user_accepted = True

    def _reject(self) -> None:
        """
        Handle the rejection of the terms and conditions.

        This method is called when the user clicks the "I Reject" button. It logs a message
        indicating that the user has rejected the terms and conditions and then closes the
        application.
        """
        self._logger.info("User has rejected the terms and conditions.")
        messagebox.showinfo("Info", "You have rejected the terms and conditions.")
        if self._window is not None:
            self._window.destroy()
        self._user_accepted = False
