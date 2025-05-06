from packageurl import PackageURL
from pydantic import BaseModel

from labels.model.package import Digest
from labels.model.release import Release


class RpmFileRecord(BaseModel):
    path: str
    mode: int
    size: int
    digest: Digest
    username: str
    group_name: str | None
    flags: str


class RpmDBEntry(BaseModel):
    id_: str
    name: str
    version: str
    epoch: int | None
    arch: str
    release: str
    source_rpm: str
    size: int
    vendor: str
    modularitylabel: str
    files: list[RpmFileRecord]


def package_url(  # noqa: PLR0913
    *,
    name: str,
    arch: str | None,
    epoch: int | None,
    source_rpm: str,
    version: str,
    release: str,
    distro: Release | None,
) -> str:
    namespace = ""
    if distro:
        namespace = distro.id_
    qualifiers: dict[str, str] = {}
    if arch:
        qualifiers["arch"] = arch
    if epoch:
        qualifiers["epoch"] = str(epoch)
    if source_rpm:
        qualifiers["upstream"] = source_rpm

    return PackageURL(
        type="rpm",
        namespace=namespace,
        name=name,
        version=f"{version}-{release}",
        qualifiers=qualifiers,
        subpath="",
    ).to_string()
