import base64
import logging

import aioboto3
import botocore

from labels.integrations.docker import get_docker_image
from labels.model.sources import AwsCredentials, AwsRole, ImageMetadata
from labels.utils.exceptions import AwsCredentialsNotFoundError

LOGGER = logging.getLogger(__name__)


async def get_credentials(credentials: AwsRole) -> AwsCredentials | None:
    try:
        async with aioboto3.Session().client(service_name="sts") as sts_client:
            response = await sts_client.assume_role(
                ExternalId=credentials.external_id,
                RoleArn=credentials.role,
                RoleSessionName="FluidAttacksRoleVerification",
            )
            aws_credentials = AwsCredentials(
                access_key_id=response["Credentials"]["AccessKeyId"],
                secret_access_key=response["Credentials"]["SecretAccessKey"],
                session_token=response["Credentials"]["SessionToken"],
            )
    except botocore.exceptions.ClientError:
        LOGGER.exception("We found problems on your AWS credentials")
        raise
    else:
        return aws_credentials


async def run_boto3_fun(  # noqa: PLR0913
    credentials: AwsCredentials,
    service: str,
    function: str,
    region: str | None = None,
    parameters: dict[str, object] | None = None,
    paginated_results_key: str | None = None,
) -> dict[str, dict | list]:
    try:
        session = aioboto3.Session(
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
        )
        async with session.client(service, region) as client:  # type: ignore[call-overload]
            if paginated_results_key and client.can_paginate(function):
                paginator = client.get_paginator(function)
                page_iterator = paginator.paginate(**(parameters or {}))
                merged_pages_list = []
                async for page in page_iterator:
                    merged_pages_list.extend(page[paginated_results_key])
                return {paginated_results_key: merged_pages_list}
            return await getattr(client, function)(**(parameters or {}))
    except botocore.exceptions.ClientError:
        LOGGER.exception("We found problems on your AWS credentials")
        raise


async def get_token(credentials: AwsCredentials) -> str:
    get_authorization_token = await run_boto3_fun(
        credentials=credentials,
        service="ecr",
        function="get_authorization_token",
    )

    auth_resp = get_authorization_token["authorizationData"][0]
    token = auth_resp["authorizationToken"]
    _username, password = base64.b64decode(token).decode("utf-8").split(":")
    return password


async def ecr_connection(
    role: AwsRole,
    image_uri: str,
) -> tuple[str, ImageMetadata]:
    credentials = await get_credentials(role)

    if not credentials:
        raise AwsCredentialsNotFoundError

    token = await get_token(credentials)
    image_ref = f"docker://{image_uri}"
    aws_creds = f"AWS:{token}"
    image_metadata = get_docker_image(
        image_ref,
        aws_creds=aws_creds,
    )

    return token, image_metadata
