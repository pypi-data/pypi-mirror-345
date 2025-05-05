"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

import os
from pathlib import Path


# Directories structure definitions
class FileStructureDirs:
    def __init__(self):
        """
        Initializes directory paths used in the file structure.
        """
        self._current_settings_dir: str = os.path.dirname(__file__)
        self._base_dir: Path = Path(
            self._current_settings_dir
        )  # Base directory for service
        self._lib = Path("lib")

        self.binary_dir_path: Path = (
            self._base_dir / self._lib
        )  # Base directory for binary storage
        os.makedirs(self.binary_dir_path, exist_ok=True)

        self.project_root = self._find_project_root()
        self.project_root_binary_dir_path = self.project_root / self._lib
        os.makedirs(self.project_root_binary_dir_path, exist_ok=True)

    def _find_project_root(self) -> Path:
        for parent in [self._base_dir] + list(self._base_dir.parents):
            if (
                (parent / "pyproject.toml").exists()
                or (parent / "requirements.txt").exists()
                or (parent / ".git").exists()
            ):
                return parent
        return self._base_dir


# File names and templates definitions
class FileStructureFiles:
    def __init__(self):
        """
        Initializes file names and templates used in the file structure.
        """
        self.binary_path: Path = Path("libpurem.so")
        self.binary_archive_path: Path = Path("libpurem.zip")
        self.binary_archive_path_tmp: Path = Path("libpurem.txt")


# Files and directories internal management
class FileStructure:
    def __init__(self):
        """
        Initializes the file structure with directories and files.
        """
        self.dirs = FileStructureDirs()
        self.files = FileStructureFiles()

    def get_binary_path(self) -> Path:
        """
        Retrieve the path for the licensed binary file.

        Returns:
            Path: Full path for the licensed binary file.
        """
        return self.dirs.binary_dir_path / Path(self.files.binary_path)

    def get_binary_archive_path(self) -> Path:
        """
        Retrieve the path for the licensed binary archive file.

        Returns:
            Path: Full path for the licensed binary archive file.
        """
        return self.dirs.binary_dir_path / Path(self.files.binary_archive_path)

    def get_binary_project_root_path(self) -> Path:
        """
        Retrieve the path for the licensed project root binary file.

        Returns:
            Path: Full path for the licensed project root binary file.
        """
        return self.dirs.project_root_binary_dir_path / Path(self.files.binary_path)

    def get_binary_archive_path_tmp(self) -> Path:
        return self.dirs.binary_dir_path / Path(self.files.binary_archive_path_tmp)
