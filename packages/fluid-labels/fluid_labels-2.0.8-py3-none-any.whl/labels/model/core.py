from enum import Enum
from typing import TypedDict

from pydantic import BaseModel


class OutputFormat(Enum):
    FLUID_JSON = "fluid-json"
    CYCLONEDX_JSON = "cyclonedx-json"
    CYCLONEDX_XML = "cyclonedx-xml"
    SPDX_JSON = "spdx-json"
    SPDX_XML = "spdx-xml"

    @classmethod
    def from_string(cls: type["OutputFormat"], value: str) -> "OutputFormat":
        for member in cls:
            if member.value == value.lower():
                return member

        error_msg = f"{value} is not a valid {cls.__name__}"
        raise ValueError(error_msg)


class SourceType(Enum):
    DIRECTORY = "dir"
    DOCKER = "docker"
    DOCKER_DAEMON = "docker-daemon"
    ECR = "ecr"

    @classmethod
    def from_string(cls: type["SourceType"], value: str) -> "SourceType":
        for member in cls:
            if member.value == value.lower():
                return member

        error_msg = f"{value} is not a valid {cls.__name__}"
        raise ValueError(error_msg)


class ScanArgs(TypedDict):
    source: str
    format: str
    output: str
    docker_user: str | None
    docker_password: str | None
    aws_external_id: str | None
    aws_role: str | None
    config: bool
    debug: bool


class DockerCredentials(TypedDict):
    username: str
    password: str


class AwsCredentials(TypedDict):
    external_id: str
    role: str


class OutputConfig(TypedDict):
    name: str
    format: str


class LoadedConfig(TypedDict):
    source: str
    source_type: str
    execution_id: str
    exclude: tuple[str]
    docker_credentials: DockerCredentials | None
    aws_credentials: AwsCredentials | None
    output: OutputConfig
    debug: bool


class SbomConfig(BaseModel):
    source: str
    source_type: SourceType
    execution_id: str | None
    output_format: OutputFormat
    output: str
    exclude: tuple[str, ...]
    docker_user: str | None = None
    docker_password: str | None = None
    aws_external_id: str | None = None
    aws_role: str | None = None
    debug: bool
