from datetime import (
    datetime,
)

import pydantic

from labels.advisories import (
    roots as advisories,
)
from labels.model.package import HealthMetadata, Package
from labels.parsers.package_information.go import (
    fetch_latest_version_info,
    fetch_license_info,
)


class GolangModuleEntry(pydantic.BaseModel):
    h1_digest: str


def _update_advisories(package: Package) -> None:
    pkg_advisories = advisories.get_vulnerabilities("go", package.name, package.version)
    if pkg_advisories:
        package.advisories = pkg_advisories


def complete_package(package: Package) -> Package:
    _update_advisories(package)
    latest = fetch_latest_version_info(package.name)
    if not latest:
        return package
    package.health_metadata = HealthMetadata(
        latest_version=latest["Version"],
        latest_version_created_at=datetime.fromisoformat(latest["Time"]),
        artifact=None,
    )
    if package.name.startswith("github.com"):
        license_info = fetch_license_info("/".join(package.name.split("/")[1:]))
        if not license_info:
            return package
        licenses = license_info["license"]["spdx_id"]
        package.licenses = [licenses]
    return package
