from copy import (
    deepcopy,
)
from typing import (
    cast,
)

from labels.model.file import (
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
from labels.parsers.collection.json import (
    parse_json_with_tree_sitter,
)
from labels.parsers.collection.types import (
    IndexedDict,
    IndexedList,
)


def format_conan_lock_dep(
    dep_info: str,
    location: Location,
    *,
    is_dev: bool = False,
) -> Package:
    product, version = dep_info.split("/")
    version = version.split("#")[0]
    location.scope = Scope.DEV if is_dev else Scope.PROD
    return Package(
        name=product,
        version=version,
        type=PackageType.ConanPkg,
        locations=[location],
        p_url=package_url(product, version),
        metadata=None,
        language=Language.CPP,
        licenses=[],
        is_dev=is_dev,
    )


def parse_conan_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    conan_file = cast(
        IndexedDict[str, IndexedList[str]],
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    for index, dep_line in enumerate(conan_file.get("requires", [])):
        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = (
                conan_file["requires"]
                .get_position(
                    index,
                )
                .start.line
            )
        packages.append(
            format_conan_lock_dep(dep_line, location),
        )
    for index, dep_line in enumerate(conan_file.get("build_requires", [])):
        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = conan_file["build_requires"].get_position(index).start.line
        packages.append(
            format_conan_lock_dep(dep_line, location, is_dev=True),
        )
    return packages, []
