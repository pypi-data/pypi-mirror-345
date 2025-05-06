import re
from copy import (
    deepcopy,
)
from typing import (
    cast,
)

from labels.model.file import (
    DependencyType,
    Location,
    LocationReadCloser,
    Scope,
)
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
)
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.cpp.package import (
    package_url,
)
from labels.parsers.cataloger.generic.parser import (
    Environment,
)


def get_conan_dep_info(dep_line: str) -> tuple[str, str]:
    product, version = re.sub(r"[\"\]\[]", "", dep_line).strip().split("@")[0].split("/")
    if "," in version:
        version = re.sub(r",(?=[<>=])", " ", version).split(",")[0]
    return product, version


def format_conan_lock_dep(
    dep_info: str,
    location: Location,
    *,
    is_dev: bool = False,
) -> Package | None:
    regex = r"^([a-zA-Z0-9\-_]+)\/([^\s@]+)"
    match = re.match(regex, dep_info)
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if match:
        name, version = cast(tuple[str, str], match.groups())
        return Package(
            name=name,
            version=version,
            type=PackageType.ConanPkg,
            locations=[location],
            p_url=package_url(name, version),
            metadata=None,
            language=Language.CPP,
            licenses=[],
            is_dev=is_dev,
        )
    return None


def build_location(
    reader: LocationReadCloser,
    line_number: int,
    *,
    is_dev: bool,
) -> Location:
    location = deepcopy(reader.location)
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        location.coordinates.line = line_number
        location.dependency_type = DependencyType.DIRECT
    return location


def parse_conan_file(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    line_deps: bool = False
    is_dev = False
    for line_number, line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        if re.search(r"^\[(tool|build)_requires\]$", line):
            line_deps = True
            is_dev = True
        elif not is_dev and line.startswith("[requires]"):
            line_deps = True
            is_dev = False
        elif line_deps:
            if not line or line.startswith("["):
                line_deps = False
                continue
            pkg_name, pkg_version = get_conan_dep_info(line)
            location = build_location(reader, line_number, is_dev=is_dev)
            packages.append(
                Package(
                    name=pkg_name,
                    version=pkg_version,
                    type=PackageType.ConanPkg,
                    locations=[location],
                    p_url=package_url(pkg_name, pkg_version),
                    metadata=None,
                    language=Language.CPP,
                    licenses=[],
                    is_dev=is_dev,
                ),
            )
    return packages, []
