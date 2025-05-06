import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.parsers.collection.types import IndexedDict, IndexedList

LOGGER = logging.getLogger(__name__)


class EnumEncoder(json.JSONEncoder):
    def default(self, item: Any) -> Any:
        if isinstance(item, Enum):
            return item.value
        if isinstance(item, IndexedList):
            return list(item.data)
        if isinstance(item, IndexedDict):
            return dict(item.data)
        if isinstance(item, BaseModel):
            return item.model_dump()
        if isinstance(item, datetime):
            return item.isoformat()
        return super().default(item)


def serialize_package(package: Package) -> dict[str, Any]:
    return {
        "id": package.id_,
        "name": package.name,
        "version": package.version,
        "locations": [
            {
                "path": loc.path(),
                "line": loc.coordinates.line if loc.coordinates and loc.coordinates.line else None,
                "layer": loc.coordinates.file_system_id
                if loc.coordinates and loc.coordinates.file_system_id
                else None,
                "dependency_type": loc.dependency_type.value,
                "scope": loc.scope.value,
                "reachable_cves": loc.reachable_cves,
            }
            for loc in package.locations
        ],
        "licenses": package.licenses,
        "type": package.type.value,
        "language": package.language.value,
        "platform": package.language.get_platform_value(),
        "package_url": package.p_url,
        "found_by": package.found_by,
        "health_metadata": package.health_metadata.model_dump()
        if package.health_metadata
        else None,
        "advisories": [adv.model_dump() for adv in package.advisories or []],
    }


def serialize_packages(packages: list[Package]) -> list[dict[str, Any]]:
    raw_pkgs = [serialize_package(pkg) for pkg in packages]
    return validate_pkgs(raw_pkgs)


def validate_pkgs(raw_sbom_pkgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pkgs_to_remove = []
    for index, raw_pkg in enumerate(raw_sbom_pkgs):
        try:
            pkg = json.loads(json.dumps(raw_pkg, cls=EnumEncoder))
            raw_sbom_pkgs[index] = pkg
        except TypeError as err:
            LOGGER.warning(
                "Cannot serialize package at index %d: %s. Error: %s",
                index,
                raw_pkg,
                str(err),
            )
            pkgs_to_remove.append(index)

    for index in sorted(pkgs_to_remove, reverse=True):
        raw_sbom_pkgs.pop(index)
    return raw_sbom_pkgs


def build_relationship_map(relationships: list[Relationship]) -> list[dict[str, str | list[str]]]:
    dependency_map: dict[str, list[str]] = {}
    for rel in relationships:
        from_pkg = rel.from_
        to_pkg = rel.to_
        ref = to_pkg.id_
        dep = from_pkg.id_
        dependency_map.setdefault(ref, []).append(dep)
    return [{"from": ref, "to": deps} for ref, deps in dependency_map.items()]


def build_sbom_metadata(namespace: str, version: str | None, timestamp: str) -> dict[str, Any]:
    return {
        "name": namespace,
        "version": version,
        "timestamp": timestamp,
        "tool": "Fluid-Labels",
        "organization": "Fluid attacks",
    }
