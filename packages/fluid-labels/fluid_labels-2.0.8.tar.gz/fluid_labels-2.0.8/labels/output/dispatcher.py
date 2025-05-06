import os
from collections.abc import Callable

from labels.advisories.match_versions import (
    convert_semver_to_range,
    is_single_version,
    match_version_ranges,
)
from labels.model.core import OutputFormat, SbomConfig
from labels.model.file import Location
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.resolver import Resolver
from labels.output.cyclonedx.output_handler import format_cyclonedx_sbom
from labels.output.fluid.output_handler import format_fluid_sbom
from labels.output.spdx.output_handler import format_spdx_sbom

_FORMAT_HANDLERS: dict[OutputFormat, Callable] = {
    OutputFormat.FLUID_JSON: format_fluid_sbom,
    OutputFormat.CYCLONEDX_JSON: format_cyclonedx_sbom,
    OutputFormat.CYCLONEDX_XML: format_cyclonedx_sbom,
    OutputFormat.SPDX_JSON: format_spdx_sbom,
    OutputFormat.SPDX_XML: format_spdx_sbom,
}


def split_version_range(v1: str, v2: str) -> tuple[str, str] | None:
    v1_single = is_single_version(convert_semver_to_range(v1))
    v2_single = is_single_version(convert_semver_to_range(v2))
    if not v1_single and v2_single:
        return v1, v2

    if not v2_single and v1_single:
        return v2, v1

    return None


def parent_dir(path: str) -> str:
    p = path.rstrip(os.sep)
    if os.sep not in p:
        return ""
    return p.rsplit(os.sep, 1)[0]


def same_directory(path1: str | None, path2: str | None) -> bool:
    if path1 is None or path2 is None:
        return False
    return parent_dir(path1) == parent_dir(path2)


def _merge_locations(target: Package, source: Package) -> None:
    for loc in source.locations:
        if loc not in target.locations:
            target.locations.append(loc)


def _find_merge_target(pkg: Package, candidates: list[Package]) -> Package | None:
    for existing in candidates:
        if existing.name != pkg.name:
            continue
        if _share_parent_dir(existing.locations, pkg.locations) and match_version_ranges(
            pkg.version,
            existing.version,
        ):
            return existing
    return None


def _share_parent_dir(locations_a: list[Location], locations_b: list[Location]) -> bool:
    return any(
        same_directory(a.access_path, b.access_path) for a in locations_a for b in locations_b
    )


def merge_packages(packages: list[Package]) -> list[Package]:
    merged: dict[str, Package] = {}
    for pkg in packages:
        if pkg.id_ in merged:
            _merge_locations(merged[pkg.id_], pkg)
            continue

        target = _find_merge_target(pkg, list(merged.values()))
        if target:
            split = split_version_range(target.version, pkg.version)
            if split:
                _, fixed_ver = split
                if fixed_ver == pkg.version:
                    _merge_locations(pkg, target)
                    del merged[target.id_]
                    merged[pkg.id_] = pkg
                    continue
            _merge_locations(target, pkg)
        else:
            merged[pkg.id_] = pkg

    return list(merged.values())


def dispatch_sbom_output(
    *,
    packages: list[Package],
    relationships: list[Relationship],
    config: SbomConfig,
    resolver: Resolver,
) -> None:
    processed_packages = merge_packages(packages)

    handler = _FORMAT_HANDLERS[config.output_format]
    handler(
        packages=processed_packages,
        relationships=relationships,
        config=config,
        resolver=resolver,
    )
