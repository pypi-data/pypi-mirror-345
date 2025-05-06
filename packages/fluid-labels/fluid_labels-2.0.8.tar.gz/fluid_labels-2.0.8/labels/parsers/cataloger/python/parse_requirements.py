import logging
from collections.abc import Generator
from contextlib import (
    suppress,
)
from copy import (
    deepcopy,
)

import requirements
from pydantic import (
    ValidationError,
)
from requirements.requirement import (
    Requirement,
)

from labels.model.file import (
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
from labels.parsers.cataloger.generic.parser import (
    Environment,
)
from labels.parsers.cataloger.python.model import (
    PythonRequirementsEntry,
)
from labels.parsers.cataloger.python.package import (
    package_url,
)
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)

OPERATOR_ORDER = {"==": 1, "===": 1, "~=": 1, ">=": 2, ">": 2, "<": 3, "<=": 3}


def get_dep_version_range(dep_specs: list[tuple[str, str]]) -> str | None:
    version_range = ""
    ordered_specs = sorted(dep_specs, key=lambda x: OPERATOR_ORDER.get(x[0], 1))
    for operator, version in ordered_specs:
        if operator not in OPERATOR_ORDER:
            return None

        if operator in {"==", "~="}:
            version_range = version
            break
        version_range += f"{operator}{version} "
    return version_range.rstrip()


def get_parsed_dependency(line: str) -> tuple[str, str, Requirement, bool] | None:
    with suppress(Exception):
        parsed_dep = next(iter(requirements.parse(line)))
        if not parsed_dep.specs or not (version := get_dep_version_range(parsed_dep.specs)):
            return None
        is_dev: bool = False
        if parsed_dep.extras and any("dev" in extra.lower() for extra in parsed_dep.extras):
            is_dev = True
        return str(parsed_dep.name), version, parsed_dep, is_dev
    return None


def split_lines_requirements(
    content: str,
) -> Generator[tuple[int, str], None, None]:
    last_line = ""
    line_number = 1
    for index, raw_line in enumerate(content.splitlines(), 1):
        if not last_line:
            line_number = index
        line = trim_requirements_txt_line(raw_line)
        if last_line != "":
            line = last_line + line
            last_line = ""
        if line.endswith("\\"):
            last_line += line.rstrip("\\")
            continue
        if not line:
            continue

        if any(
            (
                line.startswith("-e"),
                line.startswith("-r"),
                line.startswith("--requirements"),
            ),
        ):
            continue

        yield line_number, line


def parse_requirements_txt(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    line_number = 1

    try:
        content = reader.read_closer.read()
    except UnicodeDecodeError:
        return packages, []

    for line_number, line in split_lines_requirements(content):
        parsed_dep = get_parsed_dependency(line)

        # Avoid parsing big txt files that have nothing to do with pip
        if not parsed_dep:
            continue

        product, version, req, is_dev = parsed_dep

        if not product or not version:
            continue

        p_url = package_url(product, version, None)
        current_location = deepcopy(reader.location)
        if current_location.coordinates:
            current_location.scope = Scope.DEV if is_dev else Scope.PROD
            current_location.coordinates.line = line_number

        try:
            packages.append(
                Package(
                    name=product,
                    version=version,
                    found_by=None,
                    locations=[current_location],
                    language=Language.PYTHON,
                    p_url=p_url,
                    metadata=PythonRequirementsEntry(
                        name=str(req.name),
                        extras=sorted(req.extras),
                        version_constraint=",".join(f"{s[0]} {s[1]}" for s in req.specs)
                        if req.specs
                        else "",
                        markers=p_url,
                    ),
                    licenses=[],
                    type=PackageType.PythonPkg,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": current_location.path(),
                    },
                },
            )
            continue

    return packages, []


def remove_trailing_comment(line: str) -> str:
    parts = line.split("#", 1)
    if len(parts) < 2:
        # there aren't any comments
        return line
    return parts[0]


def parse_url(line: str) -> str:
    parts = line.split("@")

    if len(parts) > 1:
        desired_index = -1

        for index, raw_part in enumerate(parts):
            part = "".join([char for char in raw_part if char.isalnum()])

            if part.startswith("git"):
                desired_index = index
                break

        if desired_index != -1:
            return "@".join(parts[desired_index:]).strip()

    return ""


def trim_requirements_txt_line(line: str) -> str:
    line = line.strip()

    return remove_trailing_comment(line)
