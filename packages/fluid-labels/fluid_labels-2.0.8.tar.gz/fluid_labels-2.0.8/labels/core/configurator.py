import logging
from pathlib import Path
from typing import Unpack

import confuse

from labels.model.core import (
    LoadedConfig,
    OutputFormat,
    SbomConfig,
    ScanArgs,
    SourceType,
)
from labels.utils.exceptions import InvalidConfigFileError

LOGGER = logging.getLogger(__name__)

YAML_SCHEMA = {
    "source": confuse.String(),
    "source_type": confuse.OneOf(
        [_source.value for _source in SourceType],
    ),
    "execution_id": confuse.Optional(confuse.String(), default=None),
    "exclude": confuse.Optional(confuse.Sequence(confuse.String()), default=()),
    "docker_credentials": confuse.Optional(
        {
            "username": confuse.String(),
            "password": confuse.String(),
        },
        default={},
    ),
    "aws_credentials": confuse.Optional(
        {
            "external_id": confuse.String(),
            "role": confuse.String(),
        },
        default={},
    ),
    "output": {
        "name": confuse.String(),
        "format": confuse.OneOf(
            [_format.value for _format in OutputFormat],
        ),
    },
    "debug": confuse.Optional(confuse.OneOf([True, False]), default=False),
}

STATIC_SCAN_YAML_SCHEMA = {
    "working_dir": confuse.Optional(confuse.String(), default="./"),
    "execution_id": confuse.Optional(confuse.String(), default=None),
    "sbom": {
        "exclude": confuse.Optional(confuse.Sequence(confuse.String()), default=()),
        "output": {
            "name": confuse.String(),
            "format": confuse.OneOf(
                [_format.value for _format in OutputFormat],
            ),
        },
    },
}


def build_labels_config_from_args(arg: str, **kwargs: Unpack[ScanArgs]) -> SbomConfig:
    return SbomConfig(
        source=arg,
        source_type=SourceType.from_string(kwargs["source"]),
        execution_id=None,
        output_format=OutputFormat.from_string(kwargs["format"]),
        output=kwargs["output"],
        exclude=(),
        docker_user=kwargs["docker_user"],
        docker_password=kwargs["docker_password"],
        aws_external_id=kwargs["aws_external_id"],
        aws_role=kwargs["aws_role"],
        debug=kwargs["debug"],
    )


def build_labels_config_from_file(
    config_file_path: str,
    *,
    static_scan: bool = False,
) -> SbomConfig:
    if Path(config_file_path).is_file():
        if not config_file_path.endswith((".yaml", ".yml")):
            error_msg = "The configuration file must be a YAML format"
            raise InvalidConfigFileError(config_file_path, error_msg)
        if static_scan:
            return load_config_from_static_scan(config_file_path)
        return load_config_from_file(config_file_path)

    raise InvalidConfigFileError(config_file_path)


def load_config_from_file(config_path: str) -> SbomConfig:
    template = _build_template(config_path)
    check_unused_keys(template, set(YAML_SCHEMA.keys()))

    config_as_dict: LoadedConfig = template.get(YAML_SCHEMA)

    config_docker = config_as_dict["docker_credentials"]
    config_aws = config_as_dict["aws_credentials"]
    output = config_as_dict["output"]

    return SbomConfig(
        source=config_as_dict["source"],
        source_type=SourceType.from_string(config_as_dict["source_type"]),
        output_format=OutputFormat.from_string(output["format"]),
        output=output["name"],
        exclude=config_as_dict["exclude"],
        docker_user=config_docker["username"] if config_docker else None,
        docker_password=config_docker["password"] if config_docker else None,
        aws_external_id=config_aws["external_id"] if config_aws else None,
        aws_role=config_aws["role"] if config_aws else None,
        execution_id=config_as_dict["execution_id"],
        debug=config_as_dict["debug"],
    )


def _build_template(config_path: str) -> confuse.Configuration:
    template = confuse.Configuration("labels", read=False)
    template.set_file(config_path)
    template.read(user=False, defaults=False)
    return template


def check_unused_keys(config: confuse.Configuration, expected_keys: set[str]) -> None:
    config_keys = set(config.keys())
    unused_keys = config_keys - expected_keys
    if unused_keys:
        unrecognized_keys = ", ".join(unused_keys)
        msg = (
            f"Some keys were not recognized: {unrecognized_keys}."
            " The analysis will be performed only using the supported keys"
            " and defaults."
        )
        LOGGER.warning(msg)


def load_config_from_static_scan(config_path: str) -> SbomConfig:
    template = _build_template(config_path)
    config_as_dict = template.get(STATIC_SCAN_YAML_SCHEMA)
    labels_config = config_as_dict["sbom"]
    output = labels_config["output"]

    return SbomConfig(
        source=config_as_dict["working_dir"],
        source_type=SourceType.DIRECTORY,
        output_format=OutputFormat.from_string(output["format"]),
        output=output["name"],
        exclude=labels_config["exclude"],
        execution_id=config_as_dict["execution_id"],
        debug=config_as_dict.get("debug", False),
    )
