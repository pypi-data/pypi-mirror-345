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
from typing import Optional

from dotenv import load_dotenv  # Import dotenv
from pydantic import BaseModel, ValidationError, Field


# Loads environment variables from .env file
load_dotenv()


class EnvConfig(BaseModel):
    """
    Configuration class for environment variables validation using Pydantic.
    Each field represents a required environment variable with validation.
    """

    PUREM_LICENSE_KEY: Optional[str] = Field(
        ..., description="Purem Instance License Key."
    )
    PUREM_DOWNLOAD_BINARY_URL: Optional[str] = Field(
        default="https://api.worktif.com/binary/v2/products/purem?token=",
        description="Purem Instance Download Binary URL.",
    )
    PUREM_CONFIG_URL: Optional[str] = Field(
        ..., description="Purem Instance Binary Config URL."
    )
    PUREM_VERBOSE: bool = Field(default="none", description="Verbose Purem Mode.")
    DEBUG: bool = Field(default=False, description="Debug Mode.")


def load_env_config() -> EnvConfig:
    """
    Load and validate environment variables using the AppConfig schema.
    If validation fails, it prints the errors and raises the exception.

    Returns:
        EnvConfig: A validated instance of the configuration class.
    """
    licenced_key_default = None
    try:
        # Retrieve and validate environment variables
        return EnvConfig(
            PUREM_LICENSE_KEY=os.getenv("PUREM_LICENSE_KEY", licenced_key_default),
            PUREM_DOWNLOAD_BINARY_URL=os.getenv(
                "PUREM_DOWNLOAD_BINARY_URL",
                "https://api.worktif.com/binary/v2/products/purem?token=",
            ),
            PUREM_CONFIG_URL=os.getenv("PUREM_CONFIG_URL"),
            PUREM_VERBOSE=os.getenv("PUREM_VERBOSE", "0").strip().lower()
            in {"1", "true", "yes"},
            DEBUG=os.getenv("DEBUG", "false").strip().lower() in {"1", "true", "yes"},
        )
    except ValidationError as e:
        # Print detailed error messages for missing or invalid environment variables
        print("Configuration validation error:")
        print(e.json(indent=2))  # Format errors for better readability
        raise
