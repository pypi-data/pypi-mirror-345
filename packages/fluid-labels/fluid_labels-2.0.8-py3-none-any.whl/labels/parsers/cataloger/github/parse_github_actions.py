from copy import (
    deepcopy,
)
from typing import (
    cast,
)

from labels.model.file import (
    LocationReadCloser,
)
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
)
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.generic.parser import (
    Environment,
)
from labels.parsers.cataloger.github.package import (
    package_url,
)
from labels.parsers.collection.types import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from labels.parsers.collection.yaml import (
    parse_yaml_with_tree_sitter,
)


def _get_deps(jobs: IndexedDict[str, ParsedValue]) -> list[tuple[str, int]]:
    deps: list[tuple[str, int]] = []
    for job in jobs.values():
        if not isinstance(job, IndexedDict):
            continue
        steps = job.get("steps")
        if not isinstance(steps, IndexedList):
            continue
        for step in steps:
            if not isinstance(step, IndexedDict):
                continue
            uses = step.get("uses")
            if not isinstance(uses, str):
                continue
            deps.append((uses, step.get_key_position("name").start.line))
    return deps


def parse_github_actions_deps(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    parsed_content = cast(
        IndexedDict[str, ParsedValue],
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )
    if not parsed_content:
        return packages, []
    jobs = parsed_content.get("jobs")
    if not jobs or not isinstance(jobs, IndexedDict):
        return packages, []

    for dep, line_number in _get_deps(jobs):
        dep_info = dep.rsplit("@", 1)
        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = line_number
        if len(dep_info) == 2:
            packages.append(
                Package(
                    name=dep_info[0],
                    version=dep_info[1],
                    language=Language.GITHUB_ACTIONS,
                    licenses=[],
                    locations=[location],
                    type=PackageType.GithubActionPkg,
                    metadata=None,
                    p_url=package_url(dep_info[0], dep_info[1]),
                ),
            )
    return packages, []
