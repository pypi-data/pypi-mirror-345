"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

import ctypes
import json
import os
import shutil
import ssl
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional, Dict

import certifi as certifi
from numpy import ndarray

from purem.env_config import load_env_config, EnvConfig
from purem.file_structure import FileStructure
from purem.loader import Loader
from purem.logger import Logger


class Purem:
    """
    Represents the functionality of the Purem system, including initialization, configuration,
    and operations using a shared library binary. The class provides methods for setting up
    license keys, managing binary paths, loading configurations from a Content Delivery Network (CDN),
    and executing specific computations such as the softmax function. It handles both high-level
    configuration details and low-level interactions with binary libraries.

    :ivar _license_key: The license key used to initialize the system.
    :type _license_key: Optional[str]
    :ivar _lib: Represents the dynamically loaded shared library for performing operations.
    :type _lib: Optional[ctypes.CDLL]
    :ivar _download_binary_url: URL for downloading the binary configuration.
    :type _download_binary_url: Optional[str]
    :ivar _ctx: SSL context for establishing secure connections.
    :type _ctx: ssl.SSLContext
    :ivar _file_structure: The handler for managing binary-related paths and file structure.
    :type _file_structure: FileStructure
    :ivar _binary_path: Absolute path of the binary file used for execution.
    :type _binary_path: str
    :ivar _binary_project_root_path: Path to the binary located in the project root.
    :type _binary_project_root_path: str
    :ivar _binary_archive_path: Path where binary archives are stored.
    :type _binary_archive_path: str
    :ivar _binary_archive_path_tmp: Temporary path for binary archive operations.
    :type _binary_archive_path_tmp: str
    :ivar _env: Object holding environment configurations and variables.
    :type _env: Any
    :ivar _config_url: URL for retrieving Purem's configuration from a remote server.
    :type _config_url: str
    :ivar _loader: Loader instance for displaying runtime messages during setup and initialization.
    :type _loader: Loader
    :ivar _log: Logger instance for recording system messages and error details.
    :type _log: Logger
    """

    def __init__(self):
        """
        Represents the initialization and configuration of an environment, license key,
        and file structure required for the system's binary operations.

        :param licenced_key: Optional license key string for initializing the system.
        :type licenced_key: Optional[str]
        """
        self._lib: Optional[ctypes.CDLL] = None
        self._download_binary_url: Optional[str] = None
        self._ctx = ssl.create_default_context(cafile=certifi.where())
        self._file_structure = FileStructure()
        self._binary_path: Path = self._file_structure.get_binary_path()
        self._binary_project_root_path: Path = (
            self._file_structure.get_binary_project_root_path()
        )
        self._binary_archive_path: Path = self._file_structure.get_binary_archive_path()
        self._binary_archive_path_tmp: Path = (
            self._file_structure.get_binary_archive_path_tmp()
        )
        self._env: EnvConfig = load_env_config()
        self._license_key: Optional[str] = self._env.PUREM_LICENSE_KEY or None
        self._config_url: str = (
                self._env.PUREM_CONFIG_URL
                or "https://api.worktif.com/v2/portal/products/purem/config"
        )
        self._loader: Loader = Loader()
        self._log: Logger = Logger()
        print('self._license_key: ', self._license_key)

        if self._license_key is not None:
            self.configure(license_key=self._license_key)

    def configure(self, license_key: Optional[str] = None) -> None:
        """
        Configures the system with a given license key.

        This method sets up the license key required for initializing the system. If no
        license key is provided during configuration, the method checks if it was
        already initialized. If the license key remains unset, it raises a ValueError
        to indicate that a valid license key is mandatory for the setup.

        :raises ValueError: Raised when no valid license key is provided during
            configuration.

        :param license_key: An optional string representing the license key.
        :return: None
        """
        if self._license_key is None and license_key is not None:
            self._license_key = license_key
        if self._license_key is None:
            raise ValueError(
                self._log.info(
                    "Purem requires a valid license key to initialize.\n"
                    "You can obtain your key at https://worktif.com or through your enterprise deployment."
                )
            )

        self._set_binary()

    def softmax(self, array: ndarray) -> ndarray:
        try:
            ptr = array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            self._lib.purem(ptr, array.size)
            return array
        except Exception as e:
            raise ValueError(
                self._log.info(
                    "Purem requires a valid license key to initialize.\n"
                    "You can obtain your key at https://worktif.com or through your enterprise deployment.",
                    verbose=True
                )
            )

    def softmax_pure(self, ptr, size) -> None:
        """
        Computes the softmax function on the provided array using pure library implementation.

        This function applies the softmax transformation to the data pointed to by the
        pointer and modifies it in-place. The underlying implementation is handled
        by a pure library function call.

        :param ptr: Pointer to the data array that the softmax is to be applied on.
        :type ptr: Any
        :param size: The number of elements in the data array to be processed.
        :type size: int
        :return: None
        """
        self._lib.purem(ptr, size)

    def _build_url(self, config: dict) -> Optional[str]:
        """
        Constructs a URL based on the provided configuration dictionary. The method
        combines protocol, base URL, path, and appends a license key to generate
        a complete binary URL. If the provided configuration is None, the method
        returns None immediately.

        :param config: A dictionary containing the parts needed to construct the
            URL. The keys usually include:
            - `base_url`: The base of the URL (e.g., domain).
            - `protocol`: The URL protocol (e.g., "http" or "https").
            - `pathname`: The path to append to the base URL.
        :return: Returns the complete binary URL as a string if the configuration
            is valid. If the given configuration is None, it returns None.
        """
        if config is None:
            return None
        base = config.get("base_url", "").rstrip("/")
        protocol = config.get("protocol", "https")
        path = config.get("pathname", "").lstrip("/")
        binary_url = f"{protocol}://{base}/{path}{self._license_key}"
        return binary_url

    def _tune_binary(self) -> None:
        """
        Tunes the binary by loading the specified binary file as a shared library
        and setting up its function signatures for further use.

        This method initializes the shared library from the specified `_binary_path`
        and configures the expected argument types and return type for the `purem` function
        provided by the library.

        :raises OSError: If the library at `_binary_path` cannot be loaded by `ctypes.CDLL`.

        :rtype: None
        """
        self._lib = ctypes.CDLL(str(self._binary_path))
        self._lib.purem.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
        self._lib.purem.restype = None

    def _tune_project_root_binary(self) -> None:
        """
        Tuning the project root binary configuration.

        This private method initializes a connection to the binary library
        located at the project's root path. It achieves this by loading the
        binary through the use of the `ctypes.CDLL` method. The method also
        sets expected argument types and a return type for a specific function
        available in the shared library.

        :return: None
        """
        self._lib = ctypes.CDLL(str(self._binary_project_root_path))
        self._lib.purem.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
        self._lib.purem.restype = None

    def _load_from_latest_cdn_index(self) -> Optional[Dict]:
        """
        Attempts to load the latest configuration from a CDN index, if a config URL is provided.
        The method sends a request to the configured URL, reads its response, and parses it into
        a dictionary. If there is no configured URL or an exception occurs during the process, it
        returns None.

        :raises Exception: If an error occurs during the request or while reading the response.

        :return: A dictionary containing the parsed configuration data if the operation is
            successful, or None if no config URL is provided or an error occurs.
        :rtype: Optional[Dict]
        """
        try:
            if self._config_url is not None:
                req = urllib.request.Request(
                    self._config_url,
                )

                with urllib.request.urlopen(req, context=self._ctx) as response:
                    return json.load(response)
            else:
                return None

        except Exception:
            return None

    def _set_binary(self) -> None:
        """
        Sets and initializes the binary for the Purem runtime environment. The method ensures that a valid binary
        is available and properly configured. If a valid license key or binary is not found, the method will attempt
        to download, validate, and extract the required binary files. If initialization fails at any stage,
        appropriate errors are raised with detailed logging for debugging and support purposes.

        :param self: Represents the instance of the class.
        :type self: PuremRuntime

        :raises ValueError: Raised if a valid license key is missing and cannot proceed with initialization.
        :raises RuntimeError: Raised if the purem binary fails to load or cannot be initialized due to local issues,
            license mismatch, or any other unexpected errors.

        :return: None
        """
        if os.path.exists(self._binary_path):
            self._tune_binary()
        elif os.path.exists(self._binary_project_root_path):
            self._tune_project_root_binary()
        elif not self._license_key:
            raise ValueError(
                self._log.info(
                    "Purem requires a valid license key to initialize.\n"
                    "You can obtain your key at https://worktif.com or through your enterprise deployment."
                )
            )
        else:
            try:
                self._loader.set_message(
                    "Initializing Purem licensed runtime locally..."
                )
                self._loader.start()
                self._download_binary_url = (
                        self._build_url(self._load_from_latest_cdn_index())
                        or f"{self._env.PUREM_DOWNLOAD_BINARY_URL}{self._license_key}"
                )
                self._download_and_extract_binary()
                self._loader.stop()

            except Exception as e:
                raise RuntimeError(
                    self._log.info(
                        "We couldn't load your Purem binary at this time.\n"
                        "This may be a local issue or license mismatch.\n"
                        "Please try again – or contact us at support@worktif.com.\n"
                        "We're here to help you run at full power."
                    )
                )

            try:
                self._tune_project_root_binary()
            except Exception as e:
                raise RuntimeError(
                    self._log.info(
                        "It appears your Purem licensed binary can not be loaded. Please try again. If the problem "
                        "persists, please contact us at support@worktif.com. Thank you for your patience."
                    )
                )

    def _download_and_extract_binary(self) -> None:
        """
        Downloads a binary file from a given URL, saves it temporarily, and extracts its
        contents to a specific directory. Handles errors related to incomplete or
        corrupted downloads and archives.

        Raises runtime errors with detailed context if an issue occurs during download
        or extraction. Ensures successful extraction and logs the output location.

        :raises RuntimeError: If the download or extraction process fails due to
            corrupted archive or any other unexpected issue.
        """
        req = urllib.request.Request(
            self._download_binary_url, headers={"User-Agent": "Mozilla/5.0"}
        )

        try:
            with urllib.request.urlopen(req, context=self._ctx) as response:
                with open(self._binary_archive_path_tmp, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)

            shutil.move(self._binary_archive_path_tmp, self._binary_archive_path)
        except Exception as e:
            raise RuntimeError(
                self._log.info(
                    f"The Purem archive appears to be corrupted or incomplete.\nDetails: {e}"
                    "Please ensure the package downloaded fully and is unmodified.\n"
                    "Need help? Contact support@worktif.com – we'll assist right away.\n"
                )
            )

        try:
            with zipfile.ZipFile(self._binary_archive_path, "r") as zip_ref:
                zip_ref.extractall(
                    self._file_structure.dirs.project_root_binary_dir_path
                )
            self._log.info_new_line(
                f"Purem binary extracted to: {self._file_structure.dirs.binary_dir_path}"
            )
        except zipfile.BadZipFile as e:
            raise RuntimeError(
                self._log.info(
                    f"The Purem archive appears to be corrupted or incomplete.\nDetails: {e}"
                    "Please ensure the package downloaded fully and is unmodified.\n"
                    "Need help? Contact support@worktif.com – we'll assist right away.\n"
                )
            )

        self._binary_archive_path.unlink()

    def has_license_key(self) -> bool:
        """
        Checks if an object has a valid license key.

        This method evaluates whether the `_license_key` attribute of
        the object is not `None`, implying the presence of a license key.

        :return: Returns `True` if the `_license_key` attribute is not
            `None`, otherwise returns `False`.
        :rtype: bool
        """
        return self._license_key is not None
