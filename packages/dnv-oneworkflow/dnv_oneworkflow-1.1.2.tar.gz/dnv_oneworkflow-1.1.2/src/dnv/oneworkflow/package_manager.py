"""
The PackageManager modules offers a set of features for effective package management. It facilitates
the management of packages and related operations within Python applications.

Certificate Verification:
------------------------
A key security feature of the PackageManager class is its ability to verify the digital 
signature of packages before installation. This verification uses public key cryptography 
to ensure package authenticity and integrity.

Extracting the Public Key:
------------------------
The PackageManager class requires just the public key portion of a certificate for its
verification mechanism, not the full X.509 certificate. To update the public key:

1. Obtain the full certificate (PEM format) from a trusted source
2. Extract just the public key using OpenSSL:

   ```powershell
   # Extract only the public key from the certificate
   C:\\Users\\<username>\\AppData\\Local\\Programs\\Git\\mingw64\\bin\\openssl x509 -in dnv.cer -pubkey -noout > public_key.pem
   ```

   dnv.cer is the certificate file located in the DNV.One.Workflow.Deploymentfolder folder.

3. Update the `_get_public_key_data()` method with the contents of public_key.pem

Public Key Pinning:
------------------
The PackageManager implements "public key pinning" - a security practice where a specific
public key is trusted rather than relying on full certificate chain validation. This:
1. Simplifies the verification process
2. Reduces dependencies on external certificate authorities
3. Provides targeted security by only accepting packages signed with a specific key
4. Is appropriate for controlled environments where package sources are limited and well-known

Security Notes:
-------------
- The public key must be kept up-to-date if the signing certificates change
- If the private key is compromised, the `_get_public_key_data()` method must be updated
- This approach requires code changes to update the trusted key
"""

from __future__ import annotations

import base64
import json
import logging
import os
import shutil
import tempfile
import time
import zipfile
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, ClassVar, List, Optional, Tuple

import httpx
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from dacite import from_dict
from signify.authenticode import AuthenticodeVerificationResult, SignedPEFile
from tqdm import tqdm

# pylint: disable=relative-beyond-top-level
from ._user_agreement_manager import UserAgreementManager
from .logging_utils import set_log_level, set_log_level_async
from .repository import Repository


class PackageManager:
    """
    Manages the installation and uninstallation of packages.

    This class provides methods to install and uninstall packages.
    """

    _oc_install_path: ClassVar[str] = ""

    def __init__(self):
        """
        Initializes a new instance of the PackageManager class.
        """
        self._package_install_directory = PackageManager.get_apps_install_path()
        self._installed_packages = self._load_installed_applications_info()

        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self._log = logging.getLogger(__name__)

    @classmethod
    def get_apps_install_path(cls) -> str:
        """Class method to get the default installation path for OneCompute applications.

        Returns:
            str: The default installation path for OneCompute applications. If not set or set to an
            empty string, it defaults to the 'OneCompute' subdirectory within the '%LOCALAPPDATA%'
            environment variable on Windows, typically found at
            'C:\\\\Users\\\\<username>\\\\AppData\\\\Local'.
        """
        if not cls._oc_install_path.strip():
            cls._oc_install_path = os.path.join(
                os.environ["LOCALAPPDATA"], "OneCompute"
            )
        return cls._oc_install_path

    @classmethod
    def set_apps_install_path(cls, value: str) -> None:
        """Class method to set the default installation path for OneCompute applications.

        Args:
            value (str): The value to set for the default installation path.
        """
        if value:
            cls._oc_install_path = value

    def local_workflow_runtime_repo_url(self, repository: Repository) -> str:
        """Returns the URL of the local workflow runtime repository.

        Args:
            repository (Repository): The repository to get the URL for.

        Returns:
            str: The URL of the local workflow runtime repository.
        """
        local_workflow_runtime_url: str = (
            "https://{storage_account}.blob.core.windows.net/localworkflowruntime"
        )
        return local_workflow_runtime_url.format(storage_account=repository.value)

    async def install_package_async(
        self, package_name: str, runtime_identifier: str, repository: Repository
    ) -> bool:
        """
        Downloads and installs a package asynchronously.

        This method checks if the package directory is available and retrieves the package
        information from the server. If the package is already installed and up-to-date, no action
        is taken. Otherwise, the user is asked to accept the terms and conditions. If they agree,
        the package is downloaded and installed.

        Args:
            package_name (str): The name of the package to download and install.
            runtime_identifier (str): Specifies the runtime identifier for the package, which
                should be set to either "win-x64" or "linux-x64", depending on the operating system
                for which the package is intended to run.
            repository (Repository): The package repository.

        Returns:
            bool: True if the package was successfully installed, False otherwise.
        """
        if not self._is_directory_available(package_name):
            self._log.error(
                "Failed to install as the directory '%s' is locked by another process",
                self._get_package_install_path(package_name),
            )
            return False

        app_package_info = await self._get_package_info_from_server(
            package_name, runtime_identifier, repository
        )
        if not app_package_info:
            self._log.error(
                "Failed to install due to missing package info on the server!"
            )
            return False

        if not await self._accept_terms_and_conditions(repository):
            return False

        installed_package_info = self._get_installed_package_info(package_name)
        is_latest_version_installed = (
            installed_package_info
            and app_package_info.VersionId == installed_package_info.VersionId
        )
        if is_latest_version_installed:
            self._log.info(
                "The installed package '%s' (version %s) is the latest",
                package_name,
                app_package_info.VersionId,
            )
            return True

        if not await self._install_package(
            package_name, runtime_identifier, repository
        ):
            return False

        self._update_application_info(app_package_info)
        self._log.info("Successfully installed the package '%s'", package_name)
        return True

    def uninstall_package(self, package_name: str):
        """
        Uninstalls a package and removes the user agreement file.

        Args:
            package_name (str): The name of the package to uninstall.

        Returns:
            None
        """
        if not self._is_directory_available(package_name):
            self._log.error(
                "Failed to uninstall as the directory '%s' is locked by another process",
                self._get_package_install_path(package_name),
            )
            return

        try:
            # Remove directory and all its contents recursively
            install_path = self._get_package_install_path(package_name)
            if os.path.exists(install_path):
                shutil.rmtree(install_path)

            # Remove user agreement file
            agreement_file_path = UserAgreementManager.agreement_file_path()
            if os.path.exists(agreement_file_path):
                os.remove(agreement_file_path)
        except Exception as e:
            self._log.error(
                "Failed to uninstall package %s due to error: %s", package_name, str(e)
            )

    async def _accept_terms_and_conditions(self, repository: Repository) -> bool:
        """
        Asynchronously accepts the terms and conditions for a given repository.
        If the environment is not a build pipeline, it shows the terms and conditions and returns
        the acceptance status. In case of any exception, it logs the error and returns False.

        Args:
            repository (Repository): The repository for which to accept the terms and conditions.

        Returns:
            bool: True if the terms and conditions are accepted, False otherwise.
        """
        if os.getenv("IS_BUILD_PIPELINE", "false").lower() != "true":
            try:
                status = UserAgreementManager(repository, self._log).show()
                if not status:
                    self._log.error(
                        "You must accept the terms and conditions to install a package."
                    )
                    return False
            except Exception as ex:
                self._log.error(
                    "Failed to show the terms and conditions with error '%s'", str(ex)
                )
                return False
        return True

    async def _install_package(
        self, package_name: str, runtime_identifier: str, repository: Repository
    ) -> bool:
        try:
            future = await self._download_and_install_package_async(
                package_name, runtime_identifier, repository
            )
            # Asking for the results raises an exception if there is one set in the future
            future.result()
            return True
        except Exception as ex:
            self._log.error(
                "Failed to download and install %s with error '%s'",
                package_name,
                str(ex),
            )
        return False

    def _is_directory_available(self, package_name: str) -> bool:
        """
        Checks whether the directory for the specified package exists and it is not in use by
        another process.

        Args:
            package_name (str): The name of the package to check.

        Returns:
            bool: True if the directory for the package exists, False otherwise.
        """
        install_path = self._get_package_install_path(package_name)
        if not os.path.exists(install_path):
            return True
        new_directory_path = install_path + "_temp"
        try:
            os.rename(install_path, new_directory_path)
            os.rename(new_directory_path, install_path)
            return True
        except OSError:
            return False

    def _get_package_install_path(self, package_name: str) -> str:
        """
        Returns the package installation path.

        Args:
            package_name (str): The name of the package to check.

        Returns:
            str: The installation path of the package.
        """
        install_path = os.path.join(
            PackageManager.get_apps_install_path(), package_name
        )
        return install_path

    @set_log_level_async(logging.getLogger("httpx"), logging.WARNING)
    async def _get_package_info_from_server(
        self, package_name: str, runtime_identifier: str, repository: Repository
    ) -> Optional[_ApplicationInfo]:
        """
        Retrieves package information from the server.

        Args:
            package_name (str): The name of the package.
            runtime_identifier (str): The runtime identifier for the package.
            repository (Repository): The package repository.

        Returns:
            Optional[_ApplicationInfo]: The package information, if available; otherwise, None.
        """
        rid = runtime_identifier.replace("-", "/")
        repo_url = self.local_workflow_runtime_repo_url(repository)
        app_info_filename = f"{repo_url}/{rid}/{package_name}.ocm"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(app_info_filename)
                response.raise_for_status()
                return from_dict(_ApplicationInfo, data=response.json())
            except httpx.HTTPStatusError as ex:
                self._log.error(
                    "Failed to get the package info with error '%s'",
                    str(ex),
                )
            except Exception as ex:
                self._log.error(
                    "Failed to deserialize the package info with error '%s'", str(ex)
                )
        return None

    def _load_installed_applications_info(self) -> List[_ApplicationInfo]:
        """
        Loads information about installed applications by recursively visiting a directory and
        loading files with the ".OCM" extension.

        Returns:
            List[_ApplicationInfo]: A list of installed application information.
        """
        oc_install_path = PackageManager.get_apps_install_path()
        installed_packages: List[_ApplicationInfo] = []
        for path in Path(oc_install_path).rglob("*.ocm"):
            with path.open("r", encoding="utf-8-sig") as ocm_file:
                data = ocm_file.read()
                try:
                    app_info = from_dict(_ApplicationInfo, data=json.loads(data))
                    installed_packages.append(app_info)
                except Exception:
                    pass

        # Remove duplicates based on ApplicationId using dictionary comprehension
        installed_packages = list(
            {package.ApplicationId: package for package in installed_packages}.values()
        )
        return installed_packages

    def _update_application_info_cache(self, package_info: _ApplicationInfo):
        """
        Updates the application information cache with the provided package information.
        If the application is already in the cache, its version is updated.
        If the application is not in the cache, it is added.

        Args:
            package_info (_ApplicationInfo): The package information to update the cache with.
        """
        app_name = package_info.ApplicationId
        installed_package_info = self._get_installed_package_info(app_name)
        if installed_package_info:
            installed_package_info.VersionId = package_info.VersionId
        else:
            self._installed_packages.append(package_info)

    def _write_application_info_to_ocm_file(self, package_info: _ApplicationInfo):
        """
        Writes the provided package information to the OCM file of the application.
        The OCM file is located in the application's install path.

        Args:
            package_info (_ApplicationInfo): The package information to write to the OCM file.
        """
        app_name = package_info.ApplicationId
        file_path = os.path.join(
            PackageManager.get_apps_install_path(), app_name, f"{app_name}.ocm"
        )
        with open(file_path, "w", encoding="utf-8") as ocm_file:
            try:
                json.dump(
                    package_info, ocm_file, indent=4, cls=_ApplicationInfo.Encoder
                )
            except Exception as ex:
                raise ex

    def _update_application_info(self, package_info: _ApplicationInfo):
        """
        Updates the application information both in the cache and in the OCM file.

        Args:
            package_info (_ApplicationInfo): The package information to update with.
        """
        self._update_application_info_cache(package_info)
        self._write_application_info_to_ocm_file(package_info)

    def _get_installed_package_info(
        self, package_name: str
    ) -> Optional[_ApplicationInfo]:
        """
        Gets information about an installed package.

        Args:
            package_name (str): The name of the package.

        Returns:
            Optional[_ApplicationInfo]: The package information, if available; otherwise, None.
        """
        for package in self._installed_packages:
            if package.ApplicationId == package_name:
                return package
        return None

    @set_log_level(logging.getLogger("httpx"), logging.WARNING)
    def _download_and_install_package(
        self, package_name: str, runtime_identifier: str, repository: Repository
    ):
        """
        Downloads and installs a package.

        The method downloads and installs a package from a feed location. The package is
        identified by its name, version, and runtime identifier. The method downloads the
        package as a ZIP file, saves it to a temporary file, and then extracts it to a
        target directory. The method takes care of cleaning up temporary files and
        directories in case of any errors.

        The method first generates a download URL for the package using the package name,
        version, and runtime identifier. The `httpx` library is used to stream the package
        contents, write them to a temporary file. If any exceptions occur during the
        download, the method cleans up the temporary file and directory, and re-raises the
        exception.

        The `zipfile` library is used to extract the package contents to the target
        directory. If any exceptions occur during the extraction, the method cleans up the
        temporary file and directory, and re-raises the exception.

        Finally, the method removes the temporary directory and all its contents
        recursively using the`shutil.rmtree()` method.

        Args:
            package_name (str): The name of the package to download and install.
            runtime_identifier (str): The runtime identifier for the package.
            repository (Repository): The package repository.

        Returns:
            None
        """
        install_path = Path(self._get_package_install_path(package_name))
        new_directory_path = install_path.with_name(install_path.name + "_temp")

        # This may seem redundant, but it is actually done so that if an error occurs during the
        # installation process, the installed directory can be restored to its original state.
        if install_path.exists():
            shutil.move(install_path, new_directory_path)

        rid = runtime_identifier.replace("-", "/")
        repo_url = self.local_workflow_runtime_repo_url(repository)
        download_url = f"{repo_url}/{rid}/{package_name}.zip"

        self._log.info("Downloading the package '%s'", package_name)
        self._log.debug("Package download URL: '%s'", download_url)

        temp_file_path: Optional[Path] = None
        try:
            temp_file_path = self._download_package(download_url)
            self._log.info(
                "Downloaded the package '%s' to '%s'",
                package_name,
                temp_file_path,
            )

            self._log.info(
                "Unzipping the downloaded package '%s' from '%s'",
                package_name,
                temp_file_path,
            )
            self._extract_package(temp_file_path, str(install_path))
        except Exception as ex:
            self._log.error(
                "Failed to download or extract the package '%s' with error '%s'",
                package_name,
                ex,
            )
            if new_directory_path.exists():
                shutil.move(new_directory_path, install_path)
            raise ex
        finally:
            if temp_file_path and temp_file_path.exists():
                temp_file_path.unlink()

        if new_directory_path.exists():
            shutil.rmtree(new_directory_path)

    def _download_package(self, download_url: str) -> Path:
        """
        Downloads a package from the specified URL.

        This method sends a GET request to the download URL, streams the response, and writes it to
        a temporary file. It returns the path to the temporary file.

        Args:
            download_url (str): The URL to download the package from.

        Returns:
            Path: The path to the temporary file containing the downloaded package.
        """
        with httpx.Client() as client:
            with client.stream("GET", download_url) as response:
                response.raise_for_status()
                total_size_in_bytes = int(response.headers.get("content-length", 0))

                with tqdm(
                    total=total_size_in_bytes,
                    unit="iB",
                    unit_scale=True,
                    desc="Downloading",
                    ncols=150,
                ) as progress_bar:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        for chunk in response.iter_bytes():
                            temp_file.write(chunk)
                            progress_bar.update(len(chunk))
        return Path(temp_file.name)

    def _extract_package(self, temp_file_path: Path, install_path: str):
        """
        Extracts a package to the specified install path.

        This method opens the package as a zip file, extracts the 'wc.exe' file to a temporary
        location, and verifies its certificate. If the certificate is valid, it extracts the
        entire package, including 'wc.exe', to the install path. If the certificate is not valid,
        it raises a ValueError.

        Args:
            temp_file_path (Path): The path to the temporary file containing the package.
            install_path (str): The path to extract the package to.

        Raises:
            ValueError: If the certificate of 'wc.exe' could not be validated.
        """
        with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
            with tempfile.TemporaryDirectory() as temp_wc_dir:
                # Define the path of the file to be extracted within the zip file
                file_path = "wc.exe"

                # Extract the specified file from the zip file to the temporary directory
                zip_ref.extract(file_path, temp_wc_dir)

                # Construct the full path to the extracted file
                wc_path = os.path.join(temp_wc_dir, file_path)

                # Retrieve the public key data
                public_key_data = PackageManager._get_public_key_data()

                # Verify the certificates of the LocalWorkflowRuntime app using the public key data
                # If the verification fails, raise a ValueError
                if not self._verify_certificates(wc_path, public_key_data):
                    raise ValueError(
                        "LocalWorkflowRuntime app certificate validation failed."
                    )

                # If the certificate is valid, proceed with the extraction
                zip_ref.extractall(install_path)

    def _load_public_key(self, public_key_data: bytes) -> Optional[RSAPublicKey]:
        """
        Loads an RSA public key from the provided data.

        This method removes the header and footer from the data, decodes it from Base64, and then
        tries to load it as a DER-encoded public key. If the loaded public key is an RSA public key,
        it returns the public key. If the loaded public key is not an RSA public key, it logs an
        error message and returns None. If there is an error while loading the public key, it logs
        an error message and returns None.

        Args:
            public_key_data (bytes): The data of the public key to load.

        Returns:
            Optional[RSAPublicKey]: The loaded RSA public key, or None if the public key could not
            be loaded or is not an RSA public key.
        """
        # Remove the header and footer
        public_key_data = public_key_data.replace(b"-----BEGIN PUBLIC KEY-----", b"")
        public_key_data = public_key_data.replace(b"-----END PUBLIC KEY-----", b"")

        # Decode Base64
        public_key_bytes = base64.b64decode(public_key_data)

        # Load the public key
        try:
            public_key = serialization.load_der_public_key(
                public_key_bytes, backend=default_backend()
            )
            if isinstance(public_key, RSAPublicKey):
                return public_key

            self._log.error("The loaded public_key is not an RSA public key.")
        except ValueError as e:
            self._log.error("Error loading public key: %s", str(e))
        return None

    def _verify_certificates(self, filename: str, public_key_data: bytes) -> bool:
        """
        Verifies the certificates of a signed PE file.

        This method loads the public key from the provided data, then opens the PE file(binary file)
        and checks each certificate in it. If the public key of any certificate matches the loaded
        public key, it then verifies the certificate chain. If the verification is successful, it
        logs a success message and returns True. If the verification fails, it logs an error message
        and returns False.

        Args:
            filename (str): The path to the PE file to verify.
            public_key_data (bytes): The data of the public key to use for verification.

        Returns:
            bool: True if the verification was successful, False otherwise.
        """
        public_key = self._load_public_key(public_key_data)
        if public_key is None:
            return False

        try:
            with open(filename, "rb") as file_obj:
                pe = SignedPEFile(file_obj)
                verification_successful = False
                for signed_data in pe.signed_datas:
                    for cert in signed_data.certificates:
                        subject_public_key_bytes = cert.subject_public_key
                        subject_public_key = serialization.load_der_public_key(
                            subject_public_key_bytes, backend=default_backend()
                        )

                        # Verify the subject_public_key against the provided public key
                        if subject_public_key == public_key:
                            verification_successful = True
                            break

                if verification_successful:
                    self._log.info("Subject Public Key Verified Successfully")
                    self._log.info("Verifying Certificate Chain")
                    try:
                        result, e = PackageManager._perform_certificate_verification(
                            pe=pe
                        )
                    except Exception as ex:
                        self._log.error(
                            "Certificate Chain Verification Failed: %s", str(ex)
                        )
                        return False

                    if e or result != AuthenticodeVerificationResult.OK:
                        self._log.error(
                            "Certificate Chain Verification Failed: %s", str(e)
                        )
                        return False

                    self._log.info(result)
                    self._log.info("Certificate Chain Verified Successfully")
                else:
                    self._log.error("Subject Public Key Verification Failed")
                    return False
        except Exception as e:
            self._log.error("Error while verifying certificates: %s", str(e))
            return False

        return True

    async def _download_and_install_package_async(
        self, package_name: str, runtime_identifier: str, repository: Repository
    ) -> Future[None]:
        """
        Downloads and installs a package asynchronously.

        Args:
            package_name (str): The name of the package to download and install.
            runtime_identifier (str): The runtime identifier for the package.
            repository (Repository): The package repository.

        Returns:
            Future[None]: A future representing the asynchronous operation.
        """
        future: Future[None] = Future()
        try:
            self._download_and_install_package(
                package_name, runtime_identifier, repository
            )
            future.set_result(None)
        except Exception as ex:
            future.set_exception(ex)
        return future

    @staticmethod
    def _perform_certificate_verification(
        pe: SignedPEFile,
    ) -> Tuple[AuthenticodeVerificationResult, Optional[Exception]]:
        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Submit the blocking operation to the executor
            future = executor.submit(pe.explain_verify)

            # Create a progress bar
            # bar_format="{l_bar}{bar}" specifies that the progress bar should only include the left
            # part and the progress bar itself. The right part of the progress bar, which includes
            # the remaining time, is not included.
            with tqdm(
                total=100, desc="Verifying", bar_format="{l_bar}{bar}", ncols=100
            ) as pbar:
                while not future.done():
                    # Update the progress bar
                    pbar.update(5)
                    time.sleep(1)
                pbar.update(pbar.total - pbar.n)

            # Get the result from the blocking operation
            result, e = future.result()
        return result, e

    @staticmethod
    def _get_public_key_data() -> bytes:
        """
        Gets the data of the public key used for certificate verification.
        
        This method returns a hardcoded public key in PEM format which is used to verify
        the authenticity of package certificates through public key pinning.
        
        To update this key:
        1. Obtain a certificate in PEM format
        2. Extract just the public key using:
           openssl x509 -in dnv.cer -pubkey -noout > public_key.pem
        3. Replace the key below with the contents of public_key.pem
        
        Returns:
            bytes: The data of the public key in PEM format.
        """
        public_key_data = b"""-----BEGIN PUBLIC KEY-----
        MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAi/TN9zetr7HHjPlJ+jUn
        /sGblLbRKiADzW/l0OvCZzV6k3HUws/S2F/aASPxTxW/5qUw+w0N3vio/fMwYmTH
        KjPb10S6AwqF9mAR8I/neEZu0UsHy0asfdgUs65GNpSJrjwrkZO/6Gzh/f5vuTbz
        8Z8YXn62rZD8AVv53ABZ8SD5k6wv+fwetPnkpmXYQEczwWMo1ckr1qJHVYx1Dw5Y
        mtGrutx3g77AiuuSRXG/+PE4ZMr6IeteFhsrhNdiD3AwDi/arVskgcoUdcPLC99H
        2fx6qnWbDEeINJKJWHR4eD10zw/zU3NNt1g7OSrSrN2NnBqx6l7s+9nM+ywv31cG
        iYapRXv7erknQuFSOubJG9C6tlA2dAzXNCN9Hg0jFiRCl3uZNRsqshAh6mfh0KCk
        u52JRTr91dECDHMRJB9IfJi1yC7GRrlRV0uKrl7SOQ0NJ26S7nleT9yf3TijQ1+b
        jgrFH0w4dfwvrLOiLRbaBoYfCpub+E1qRA6n61OyerIyV1/lP8pVX9UYaaIyWy/d
        KkgOgEpouCeNU/aubE/rr3TOC1B5tRFmOgr42ZpBOVkYMP1ygqKtdIc1rFaWuIgD
        Fod5BE3ouSuqIn4uqW/gJVuGRulmdlh4Xk2fqnZ27cp7uncdKsWqsjo5kdK7ooa8
        jOgryMCRptamvOBdaD5PQQ0CAwEAAQ==
        -----END PUBLIC KEY-----
        """
        return public_key_data


@dataclass
class _ApplicationInfo:
    """
    Information about an application.
    """

    ApplicationId: str
    """
    Gets or sets the ID of the application.
    """

    VersionId: str
    """
    Gets or sets the ID of the package version.
    """

    ExecutablePath: str
    """
    The path to the executable file of the application.
    """

    ExecutableType: str
    """
    The type of the executable file of the application.
    """

    class Encoder(json.JSONEncoder):
        """
        Custom JSON encoder that can be used to serialize instances of the _ApplicationInfo class.
        """

        def default(self, o: Any):
            """
            Overrides the default method of the JSONEncoder class.

            Args:
                o (Any): The object to encode.

            Returns:
                Any: The encoded object.
            """
            if isinstance(o, _ApplicationInfo):
                return asdict(o)
            return super().default(o)
