import asyncio

from labels.integrations.docker import get_docker_image, get_image_context
from labels.integrations.ecr import ecr_connection
from labels.model.core import SbomConfig, SourceType
from labels.model.sources import AwsRole, ImageMetadata
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.utils.exceptions import (
    AwsExternalIdNotDefinedError,
    AwsRoleNotDefinedError,
    UnexpectedSBOMSourceError,
)


def _get_async_ecr_connection(role: AwsRole, source: str) -> tuple[str, ImageMetadata]:
    return asyncio.run(ecr_connection(role, source))


def _handle_directory(sbom_config: SbomConfig) -> Directory:
    return Directory(
        root=sbom_config.source,
        exclude=sbom_config.exclude,
    )


def _handle_docker(*, sbom_config: SbomConfig, is_daemon: bool = False) -> ContainerImage:
    docker_image = get_docker_image(
        sbom_config.source,
        username=sbom_config.docker_user,
        password=sbom_config.docker_password,
        daemon=is_daemon,
    )

    context = get_image_context(
        image=docker_image,
        username=sbom_config.docker_user,
        password=sbom_config.docker_password,
        daemon=is_daemon,
    )

    return ContainerImage(
        img=docker_image,
        context=context,
        lazy=False,
    )


def _handle_ecr(sbom_config: SbomConfig) -> ContainerImage:
    if not sbom_config.aws_role:
        raise AwsRoleNotDefinedError

    if not sbom_config.aws_external_id:
        raise AwsExternalIdNotDefinedError

    role = AwsRole(
        external_id=sbom_config.aws_external_id,
        role=sbom_config.aws_role,
    )

    token, image_metadata = _get_async_ecr_connection(
        role=role,
        source=sbom_config.source,
    )

    context = get_image_context(
        image=image_metadata,
        aws_creds=f"AWS:{token}",
    )

    return ContainerImage(
        img=image_metadata,
        context=context,
        lazy=False,
    )


def resolve_sbom_source(sbom_config: SbomConfig) -> Directory | ContainerImage:
    match sbom_config.source_type:
        case SourceType.DIRECTORY:
            return _handle_directory(sbom_config)
        case SourceType.DOCKER:
            return _handle_docker(sbom_config=sbom_config)
        case SourceType.DOCKER_DAEMON:
            return _handle_docker(sbom_config=sbom_config, is_daemon=True)
        case SourceType.ECR:
            return _handle_ecr(sbom_config)
        case _:
            raise UnexpectedSBOMSourceError(sbom_config.source_type)
