from typing import NotRequired, TypedDict

import requests

from labels.config.cache import dual_cache


class Author(TypedDict):
    name: str
    homepage: str
    email: NotRequired[str]


class Source(TypedDict):
    url: str
    type: str
    reference: str


class Dist(TypedDict):
    url: str
    type: str
    shasum: str
    reference: str


class PackagistPackageInfo(TypedDict, total=False):
    name: str
    description: str
    keywords: list[str]
    homepage: str
    version: str
    version_normalized: str
    license: list[str]
    authors: list[Author]
    source: Source
    dist: Dist
    type: str
    support: dict[str, str]
    funding: list[str]
    time: str
    autoload: dict[str, list[str]]
    extra: dict[str, dict[str, str]]
    require: dict[str, str]
    require_dev: dict[str, str]
    suggest: dict[str, str]
    conflict: dict[str, str]


class PackagistResponse(TypedDict, total=False):
    minified: str
    packages: dict[str, list[PackagistPackageInfo]]


@dual_cache
def get_composer_package(
    package_name: str,
    version: str | None = None,
) -> PackagistPackageInfo | None:
    base_url = f"https://repo.packagist.org/p2/{package_name}.json"
    response = requests.get(base_url, timeout=30)
    if response.status_code != 200:
        return None

    response_data: PackagistResponse = response.json()
    package_versions: list[PackagistPackageInfo] = response_data.get("packages", {}).get(
        package_name,
        [],
    )

    if version:
        for version_data in package_versions:
            if version_data.get("version") == version:
                return version_data
        return None

    if package_versions:
        return package_versions[0]

    return None
