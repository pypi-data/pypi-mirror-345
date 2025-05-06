from typing import TypedDict, cast

import requests

from labels.config.cache import dual_cache


class NugetCatalogEntry(TypedDict, total=False):
    authors: str
    created: str
    description: str
    id: str
    isPrerelease: bool
    lastEdited: str
    licenseExpression: str
    listed: bool
    packageHash: str
    packageHashAlgorithm: str
    packageSize: int
    projectUrl: str
    published: str
    requireLicenseAcceptance: bool
    title: str
    verbatimVersion: str
    version: str
    tags: list[str]


@dual_cache
def get_nuget_package(package_name: str, version: str | None = None) -> NugetCatalogEntry | None:
    package_name = package_name.lower()
    base_url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name}"
    if version:
        base_url += f"/{version}"
    else:
        base_url += "/index"
    base_url += ".json"
    response = requests.get(base_url, timeout=30)
    if response.status_code != 200:
        return None

    package_data = response.json()

    if version:
        catalog_url = package_data.get("catalogEntry")
        if not isinstance(catalog_url, str):
            return None
        package_data = requests.get(catalog_url, timeout=30).json()
    else:
        items = package_data.get("items")
        if not isinstance(items, list) or not items:
            return None
        last_item = items[-1]
        items_url = last_item.get("@id")
        if not isinstance(items_url, str):
            return None
        items_response = requests.get(items_url, timeout=30).json()
        items_list = items_response.get("items", [])
        try:
            package_data = next(
                x["catalogEntry"] for x in reversed(items_list) if "catalogEntry" in x
            )
        except StopIteration:
            package_data = next(
                (
                    y["catalogEntry"]
                    for x in reversed(items_list)
                    for y in reversed(x.get("items", []))
                    if "catalogEntry" in y and "pre" not in y["catalogEntry"].get("version", "")
                ),
                None,
            )

    if package_data is None:
        return None

    return cast(NugetCatalogEntry, package_data)
