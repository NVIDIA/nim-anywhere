# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Configuration options for the chat ui."""

import logging
import os
from enum import Enum
from typing import Annotated

from confz import BaseConfig, EnvSource, FileSource
from pydantic import Field, FilePath, HttpUrl, field_validator

_ENV_VAR_PREFIX = "APP_"
_CONFIG_FILE_ENV_VAR: str = f"{_ENV_VAR_PREFIX}CONFIG"


class LogLevels(Enum):
    """Options for the logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Configuration(BaseConfig):
    """Configuration for this microservice."""

    # configuration fields
    chain_url: Annotated[
        HttpUrl,
        Field(
            "http://localhost:3030/",
            description="The URL to the chain on the chain server.",
        ),
    ]

    proxy_prefix: Annotated[
        str,
        Field(
            os.environ.get("PROXY_PREFIX", "") + "/",
            description="The url prefix when this is running behind a proxy.",
            json_schema_extra={"extra_env_vars": ["PROXY_PREFIX"]},
        ),
    ]

    chain_config_file: Annotated[
        FilePath,
        Field(
            "./config.yaml",
            description="Path to the chain server's config.",
        ),
    ]

    @field_validator("proxy_prefix", mode="after")
    @classmethod
    def _check_proxy_prefix(cls, val: str) -> str:
        """Validate the proxy prefix input and ensure it has a trailing slash."""
        if not val.endswith("/"):
            val += "/"
        return val

    log_level: Annotated[LogLevels, Field(LogLevels.INFO, description=LogLevels.__doc__)]

    # sources where config is looked for
    CONFIG_SOURCES = [
        FileSource(file="./frontend-config.yaml", optional=True),
        FileSource(file="./frontend-config.yml", optional=True),
        FileSource(file="./frontend-config.json", optional=True),
        FileSource(file="/etc/frontend-app.yaml", optional=True),
        FileSource(file="/etc/frontend-app.yml", optional=True),
        FileSource(file="/etc/frontend-app.json", optional=True),
        FileSource(file_from_env=_CONFIG_FILE_ENV_VAR, optional=True),
        EnvSource(allow_all=True, prefix=_ENV_VAR_PREFIX, nested_separator="__"),
    ]

    # automatically set log level on config load
    @field_validator("log_level", mode="after")
    @classmethod
    def _check_log_level(cls, val: LogLevels) -> LogLevels:
        """Configure the default loggers."""
        logging.basicConfig()
        log_level = logging.getLevelName(val.value)
        loggers = [logging.getLogger()] + [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict
            if not (name.startswith("uvicorn") or name.startswith("aiohttp"))
        ]
        for logger in loggers:
            logger.setLevel(log_level)
        return val


# load the runtime configuration
config = Configuration()
