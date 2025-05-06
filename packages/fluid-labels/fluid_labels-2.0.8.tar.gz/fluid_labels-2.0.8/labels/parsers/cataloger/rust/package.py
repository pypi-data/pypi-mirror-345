from packageurl import (
    PackageURL,
)

from labels.advisories import (
    roots as advisories,
)
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.parsers.cataloger.common import (
    infer_algorithm,
)
from labels.parsers.licenses.validation import (
    validate_licenses,
)
from labels.parsers.package_information.rust import (
    CRATES_ENDPOINT,
    CargoPackage,
    Version,
    get_cargo_package,
)


def package_url(name: str, version: str) -> str:
    return PackageURL(  # type: ignore
        type="cargo",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def _get_artifact(
    current_package: Version | None,
) -> Artifact | None:
    if current_package:
        digest_value = current_package.get("checksum")
        return Artifact(
            url=f"{CRATES_ENDPOINT}{current_package['dl_path']}",
            integrity=Digest(
                algorithm=infer_algorithm(digest_value),
                value=digest_value,
            ),
        )
    return None


def _set_health_metadata(
    package: Package,
    current_package: Version | None,
    cargo_package: CargoPackage,
) -> None:
    crate_info = cargo_package.get("crate", {})
    max_stable_version = crate_info.get("max_stable_version")
    updated_at = crate_info.get("updated_at")
    published_by = cargo_package["versions"][0].get("published_by")

    package.health_metadata = HealthMetadata(
        latest_version=max_stable_version,
        latest_version_created_at=updated_at,
        artifact=_get_artifact(current_package),
        authors=published_by["name"] if published_by else None,
    )


def _update_advisories(package: Package) -> None:
    pkg_advisories = advisories.get_vulnerabilities("cargo", package.name, package.version)
    if pkg_advisories:
        package.advisories = pkg_advisories


def complete_package(package: Package) -> Package:
    _update_advisories(package)
    cargo_package = get_cargo_package(package.name)
    if not cargo_package:
        return package

    versions = cargo_package["versions"]
    current_package = next(
        (version for version in versions if version["num"] == package.version),
        None,
    )

    _set_health_metadata(package, current_package, cargo_package)

    licenses = versions[0].get("license")
    if isinstance(licenses, str):
        package.licenses = validate_licenses([licenses])

    return package
