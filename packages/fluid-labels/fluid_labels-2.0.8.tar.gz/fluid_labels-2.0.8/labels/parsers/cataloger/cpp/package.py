from packageurl import (
    PackageURL,
)

from labels.advisories import (
    roots as advisories,
)
from labels.model.package import Package


def package_url(name: str, version: str) -> str:
    return PackageURL(  # type: ignore
        type="conan",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def _update_advisories(package: Package) -> None:
    pkg_advisories = advisories.get_vulnerabilities("conan", package.name, package.version)
    if pkg_advisories:
        package.advisories = pkg_advisories


def complete_package(package: Package) -> Package:
    _update_advisories(package)

    return package
