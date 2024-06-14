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

"""Application Configuration

The Chain Server can be configured with either a configuration file or environment variables.

## Config from a file

By default, the application will search for a configuration file in all of the following locations.
If multiple configuration files are found, values from lower files in the list will take precendence.

  - ./config.yaml
  - ./config.yml
  - ./config.json
  - ~/app.yaml
  - ~/app.yml
  - ~/app.json
  - /etc/app.yaml
  - /etc/app.yml
  - /etc/app.json

## Config from a custom file

An additional config file path can be specified through an environment variable named `APP_CONFIG`.
The value in this file will take precedence over all the default file locations.

```bash
export APP_CONFIG=/etc/my_config.yaml
```

## Config from env vars

Configuration can also be set using environment variables.
The variable names will be in the form: `APP_FIELD__SUB_FIELD`
Values specified as environment variables will take precedence over all values from files.

"""

import logging
import os
from enum import Enum
from typing import Annotated, Callable, Optional, cast

from confz import BaseConfig, EnvSource, FileSource
from pydantic import BaseModel, Field, HttpUrl, RedisDsn, field_validator

_ENV_VAR_PREFIX = "APP_"
_CONFIG_FILE_ENV_VAR: str = f"{_ENV_VAR_PREFIX}CONFIG"


class LogLevels(Enum):
    """Options for the logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MilvusConfig(BaseModel):
    """The configuration of the Milvus vector db connection."""

    url: str = Field(
        "http://localhost:19530",
        description="The host machine running Milvus vector DB.",
    )
    collection_name: str = Field("collection_1", description="The name of the Milvus collection.")


class ChatModelConfig(BaseModel):
    """Configuration for connecting the an LLM chat model."""

    name: Annotated[
        str,
        Field(
            "meta/llama3-70b-instruct",
            description="The name of the model to request.",
        ),
    ]
    url: Annotated[
        HttpUrl,
        Field(
            "https://integrate.api.nvidia.com/v1",
            description="The URL to the model API.",
        ),
    ]


class EmbeddingModelConfig(BaseModel):
    """Configuration for connecting to an embedding model."""

    name: Annotated[
        str,
        Field(
            "NV-Embed-QA",
            description="The name of the model to request.",
        ),
    ]
    # url: Annotated[
    #     HttpUrl,
    #     Field(
    #         "https://api.nvcf.nvidia.com/v2/nvcf",
    #         description="The URL to the model API.",
    #     ),
    # ]


class Configuration(BaseConfig):
    """Configuration for this microservice."""

    # configuration fields
    nvidia_api_key: Annotated[
        Optional[str],
        Field(
            os.environ.get("NGC_API_KEY"),
            description="Your API key for authentication to AI Foundation.",
            json_schema_extra={"extra_env_vars": ["NGC_API_KEY", "NVIDIA_API_KEY"]},
        ),
    ]
    redis_dsn: Annotated[
        RedisDsn,
        Field(
            "redis://localhost:6379/0",
            description="The Data Source Name for your Redis DB.",
        ),
    ]
    chat_model: Annotated[
        ChatModelConfig,
        Field(default_factory=ChatModelConfig, description=ChatModelConfig.__doc__),
    ]
    embedding_model: Annotated[
        EmbeddingModelConfig,
        Field(
            default_factory=EmbeddingModelConfig,
            description=EmbeddingModelConfig.__doc__,
        ),
    ]
    milvus: Annotated[
        MilvusConfig,
        Field(default_factory=cast(Callable[[], MilvusConfig], MilvusConfig)),
    ]
    log_level: Annotated[LogLevels, Field(LogLevels.WARNING, description=LogLevels.__doc__)]

    # sources where config is looked for
    CONFIG_SOURCES = [
        FileSource(file="./config.yaml", optional=True),
        FileSource(file="./config.yml", optional=True),
        FileSource(file="./config.json", optional=True),
        FileSource(file="~/app.yaml", optional=True),
        FileSource(file="~/app.yml", optional=True),
        FileSource(file="~/app.json", optional=True),
        FileSource(file="/etc/app.yaml", optional=True),
        FileSource(file="/etc/app.yml", optional=True),
        FileSource(file="/etc/app.json", optional=True),
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
            for name in logging.root.manager.loggerDict  # pylint: disable=no-member
            if not (name.startswith("uvicorn") or name.startswith("aiohttp"))
        ]
        for logger in loggers:
            logger.setLevel(log_level)
        return val


# load the runtime configuration
config = Configuration()
