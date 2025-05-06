import logging
from typing import TYPE_CHECKING

from labels.model.file import Scope
from labels.utils.strings import format_exception

if TYPE_CHECKING:
    from collections.abc import ItemsView

from pydantic import ValidationError

from labels.model.file import DependencyType, Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.resolver import Resolver
from labels.parsers.cataloger.generic.parser import Environment
from labels.parsers.cataloger.python.package import package_url
from labels.parsers.collection.toml import parse_toml_with_tree_sitter
from labels.parsers.collection.types import IndexedDict, ParsedValue

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, scope: Scope) -> Location:
    location.scope = scope
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        location.dependency_type = DependencyType.DIRECT
        return location.model_copy(update=l_upd)
    return location


def _get_version(value: ParsedValue) -> str | None:
    if isinstance(value, str):
        return value
    if not isinstance(value, IndexedDict):
        return None
    version: str = str(value.get("version", ""))
    return version


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    packages: list[Package] = []

    items: ItemsView[str, ParsedValue] = dependencies.items()

    for name, value in items:
        version = _get_version(value)
        if not name or not version:
            continue

        location = _get_location(
            reader.location,
            dependencies.get_key_position(name).start.line,
            scope=Scope.DEV if is_dev else Scope.PROD,
        )

        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[location],
                    language=Language.PYTHON,
                    licenses=[],
                    p_url=package_url(
                        name=name,
                        version=version,
                        package=None,
                    ),
                    type=PackageType.PythonPkg,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": location.path(),
                    },
                },
            )
            continue

    return packages


def parse_pyproject_toml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = parse_toml_with_tree_sitter(reader.read_closer.read())

    tool: ParsedValue = content.get("tool")
    if not isinstance(tool, IndexedDict):
        return [], []

    poetry: ParsedValue = tool.get("poetry")
    if not isinstance(poetry, IndexedDict):
        return [], []

    deps: ParsedValue = poetry.get("dependencies")
    if not isinstance(deps, IndexedDict):
        return [], []

    packages = _get_packages(reader, deps)
    group: ParsedValue = poetry.get("group")
    if isinstance(group, IndexedDict):
        dev: ParsedValue = group.get("dev")
        if isinstance(dev, IndexedDict):
            dev_deps: ParsedValue = dev.get("dependencies")
            if isinstance(dev_deps, IndexedDict):
                packages.extend(_get_packages(reader, dev_deps, is_dev=True))
    return packages, []
