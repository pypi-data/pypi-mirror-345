import logging
import re
from contextlib import (
    suppress,
)
from copy import (
    deepcopy,
)
from pathlib import Path
from typing import (
    TextIO,
)

from bs4 import (
    BeautifulSoup,
    NavigableString,
    Tag,
)
from pydantic import (
    BaseModel,
    ValidationError,
)

from labels.model.file import (
    DependencyType,
    Location,
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
from labels.parsers.cataloger.java.maven_repo_utils import (
    recursively_find_versions_from_parent_pom,
)
from labels.parsers.cataloger.java.model import (
    JavaArchive,
    JavaPomParent,
    JavaPomProject,
    JavaPomProperties,
)
from labels.parsers.cataloger.java.package import (
    package_url,
)
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def get_pom_project(content: TextIO) -> Tag | None:
    if (
        (root := BeautifulSoup(content, features="html.parser"))
        and (pom_project := root.project)
        and (xmlns := root.project.get("xmlns"))
        and str(xmlns) == "http://maven.apache.org/POM/4.0.0"
    ):
        return pom_project
    return None


class ParsedPomProject(BaseModel):
    java_pom_project: JavaPomProject
    licenses: list[str]


def extract_bracketed_text(item: str) -> str:
    match = re.search(r"\$\{([^}]+)\}", item)
    if match:
        return match.group(1)
    return ""


def _get_text(parent: Tag | NavigableString, name: str) -> str | None:
    element = parent.find_next(name)
    if element:
        return element.get_text()
    return None


def _get_parent_info(project: Tag) -> dict[str, str] | None:
    if (
        (parent := project.find_next("parent"))
        and (parent_groupid_node := parent.find_next("groupid"))
        and (parent_artifactid_node := parent.find_next("artifactid"))
        and (parent_version_node := parent.find_next("version"))
    ):
        return {
            "group": parent_groupid_node.get_text(),
            "artifact": parent_artifactid_node.get_text(),
            "version": parent_version_node.get_text(),
        }
    return None


def _is_parent_pom(root_pom_project: Tag, parent_info: dict[str, str]) -> bool:
    group = root_pom_project.find("groupid", recursive=False)
    artifact = root_pom_project.find("artifactid", recursive=False)
    version = root_pom_project.find("version", recursive=False)
    if not (group and artifact and version):
        return False
    return (
        group.get_text() == parent_info["group"]
        and artifact.get_text() == parent_info["artifact"]
        and version.get_text() == parent_info["version"]
    )


def _is_module_parent(parent_pom: Tag, pom_module: str) -> bool:
    base_module = Path(pom_module).parent.name
    for modules in parent_pom.find_all("modules"):
        for module in modules.find_all("module"):
            mod_name = module.get_text()
            if mod_name == base_module:
                return True
    return False


def _get_properties(project_pom: Tag) -> dict[str, str]:
    return {
        _property.name.lower(): _property.get_text()
        for properties in project_pom.find_all("properties", limit=2)
        for _property in properties.children
        if isinstance(_property, Tag)
    }


def _get_deps_management(pom_tree: Tag) -> dict[str, str]:
    deps_info: dict[str, str] = {}
    for manage in pom_tree.find_all("dependencymanagement"):
        for dependency in manage.find_all("dependency", recursive=True):
            if not (dependency.groupid and dependency.artifactid and dependency.version):
                continue

            group = dependency.groupid.get_text()
            artifact = dependency.artifactid.get_text()
            version = dependency.version.get_text()
            deps_info[f"{group}:{artifact}"] = version
    return deps_info


def _evaluate_pom_files_in_project(
    resolver: Resolver,
    parent_info: dict[str, str],
    current_pom_file_path: str,
    current_pom_project: Tag,
) -> tuple[dict[str, str], dict[str, str]]:
    properties_vars: dict[str, str] = {}
    manage_deps: dict[str, str] = {}
    for pom_file_location in resolver.files_by_glob("**/pom.xml", "pom.xml"):
        content = resolver.file_contents_by_location(pom_file_location)
        if (
            content
            and (pom_project := get_pom_project(content))
            and _is_parent_pom(pom_project, parent_info)
            and _is_module_parent(pom_project, current_pom_file_path)
        ):
            properties_vars = _get_properties(pom_project)
            manage_deps = _get_deps_management(pom_project)
            break

    manage_deps.update(_get_deps_management(current_pom_project))
    return properties_vars, manage_deps


def is_version_correct(version: str | None) -> bool:
    return version is not None and not version.startswith("${")


def update_location_with_dependency_info(location: Location, dependency: Tag) -> None:
    if location.coordinates:
        location.coordinates.line = (
            dependency.version.sourceline if dependency.version else dependency.sourceline
        )
        location.dependency_type = DependencyType.DIRECT


def new_package_from_pom_xml(
    project: Tag,
    dependency: Tag,
    location: Location,
    parent_info: dict[str, str] | None,
    parent_version_properties: dict[str, str] | None,
) -> Package | None:
    name = _get_text(dependency, "artifactid")

    if not name:
        return None

    group_id = _get_text(dependency, "groupid")
    full_name = group_id + ":" + name if group_id else name

    java_archive = JavaArchive(
        pom_properties=JavaPomProperties(
            group_id=group_id,
            artifact_id=_get_text(dependency, "artifactid"),
            version=_get_text(dependency, "version") if dependency.version else None,
        ),
    )

    version = dependency.version.get_text() if dependency.version else None
    if (
        version
        and version.startswith("${")
        and (
            parent_version_node := project.find_next(
                extract_bracketed_text(version),
            )
        )
    ):
        version_text = parent_version_node.get_text()
        if version_text and not version_text.startswith("${"):
            version = version_text

    if version and version.startswith("${") and parent_info and parent_version_properties:
        version = parent_version_properties.get(extract_bracketed_text(version), None)

    if (
        not version
        and parent_info
        and java_archive.pom_properties
        and java_archive.pom_properties.group_id
        and java_archive.pom_properties.artifact_id
    ):
        version = recursively_find_versions_from_parent_pom(
            group_id=java_archive.pom_properties.group_id,
            artifact_id=java_archive.pom_properties.artifact_id,
            parent_group_id=parent_info["group"],
            parent_artifact_id=parent_info["artifact"],
            parent_version=parent_info["version"],
        )

    if not is_version_correct(version):
        return None

    update_location_with_dependency_info(location, dependency)

    try:
        return Package(
            name=full_name,
            version=str(version),
            licenses=[],
            locations=[location],
            language=Language.JAVA,
            type=PackageType.JavaPkg,
            metadata=java_archive,
            p_url=package_url(name, str(version), java_archive),
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
        return None


def parse_pom_xml(
    resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    root = None
    with suppress(UnicodeError):
        try:
            root = BeautifulSoup(reader.read_closer, features="html.parser")
        except AssertionError:
            return [], []

    if not root:
        return [], []

    pkgs = []
    if (
        (project := root.project)
        and str(project.get("xmlns")) == "http://maven.apache.org/POM/4.0.0"
        and (dependencies := project.find("dependencies", recursive=False))
        and isinstance(dependencies, Tag)
    ):
        parent_info = _get_parent_info(project)
        parent_version_properties = None
        if resolver and parent_info:
            parent_version_properties, _ = _evaluate_pom_files_in_project(
                resolver,
                parent_info,
                str(reader.location.access_path),
                project,
            )

        for dependency in dependencies.find_all("dependency"):
            pkg = new_package_from_pom_xml(
                project,
                dependency,
                deepcopy(reader.location),
                parent_info,
                parent_version_properties,
            )
            if pkg:
                pkgs.append(pkg)
    return pkgs, []


def decode_pom_xml(content: str) -> Tag:
    return BeautifulSoup(content, features="html.parser")


def pom_parent(parent: Tag | None) -> JavaPomParent | None:
    if not parent:
        return None

    group_id = _get_text(parent, "groupId")
    artifact_id = _get_text(parent, "artifactId")
    version = _get_text(parent, "version")
    if not group_id or not artifact_id or not version:
        return None

    result = JavaPomParent(
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
    )

    if not result.group_id and not result.artifact_id and not result.version:
        return None

    return result


def parse_pom_xml_project(
    path: str,
    reader: str,
    _location: Location,
) -> ParsedPomProject | None:
    project = BeautifulSoup(reader, features="xml").project
    if not project:
        return None
    return new_pom_project(path, project, _location)


def _find_direct_child(parent: Tag, tag: str) -> Tag | None:
    return next(
        (child for child in parent.find_all(tag, recursive=False) if child.parent == parent),
        None,
    )


def new_pom_project(
    path: str,
    project: Tag,
    _location: Location,
) -> ParsedPomProject:
    artifact_id = _safe_string(_find_direct_child(project, "artifactId"))
    name = _safe_string(_find_direct_child(project, "name"))
    project_url = _safe_string(_find_direct_child(project, "url"))

    licenses: list[str] = []
    if project.licenses:
        for license_ in project.licenses.find_all("license"):
            license_name: str | None = None
            license_url: str | None = None
            if name_node := license_.find_next("name"):
                license_name = name_node.get_text()
            elif url_node := license_.find_next("url"):
                license_url = url_node.get_text()

            if not license_name and not license_url:
                continue
            if license_name:
                licenses.append(license_name)
            elif license_url:
                licenses.append(license_url)

    return ParsedPomProject(
        java_pom_project=JavaPomProject(
            path=path,
            parent=pom_parent(_find_direct_child(project, "parent")),
            group_id=_safe_string(_find_direct_child(project, "groupId")),
            artifact_id=artifact_id,
            version=_safe_string(_find_direct_child(project, "version")),
            name=name,
            description=_safe_string(
                _find_direct_child(project, "description"),
            ),
            url=project_url,
        ),
        licenses=licenses,
    )


def _safe_string(value: Tag | None) -> str:
    if not value:
        return ""
    return value.get_text()
