import logging
from typing import TYPE_CHECKING, cast

from pydantic import (
    ValidationError,
)

from labels.model.advisories import Advisory
from labels.model.file import Location
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.parsers.cataloger.alpine import (
    package as package_alpine,
)
from labels.parsers.cataloger.cpp import (
    package as package_cpp,
)
from labels.parsers.cataloger.dart import (
    package as package_dart,
)
from labels.parsers.cataloger.debian import (
    package as package_debian,
)
from labels.parsers.cataloger.dotnet import (
    package as package_dotnet,
)
from labels.parsers.cataloger.elixir import (
    package as package_elixir,
)
from labels.parsers.cataloger.github import (
    package as package_github,
)
from labels.parsers.cataloger.golang import (
    package as package_go,
)
from labels.parsers.cataloger.java import (
    package as package_java,
)
from labels.parsers.cataloger.javascript import (
    package as package_js,
)
from labels.parsers.cataloger.php import (
    package as package_php,
)
from labels.parsers.cataloger.python import (
    package as package_python,
)
from labels.parsers.cataloger.ruby import (
    package as package_ruby,
)
from labels.parsers.cataloger.rust import (
    package as package_rust,
)
from labels.parsers.cataloger.swift import (
    package as package_swift,
)
from labels.utils.strings import format_exception

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)


def complete_package(package: Package) -> Package | None:
    completion_map: dict[PackageType, Callable[[Package], Package]] = {
        PackageType.NpmPkg: package_js.complete_package,
        PackageType.DartPubPkg: package_dart.complete_package,
        PackageType.DotnetPkg: package_dotnet.complete_package,
        PackageType.JavaPkg: package_java.complete_package,
        PackageType.PhpComposerPkg: package_php.complete_package,
        PackageType.PythonPkg: package_python.complete_package,
        PackageType.GemPkg: package_ruby.complete_package,
        PackageType.RustPkg: package_rust.complete_package,
        PackageType.DebPkg: package_debian.complete_package,
        PackageType.ApkPkg: package_alpine.complete_package,
        PackageType.GoModulePkg: package_go.complete_package,
        PackageType.HexPkg: package_elixir.complete_package,
        PackageType.ConanPkg: package_cpp.complete_package,
        PackageType.GithubActionPkg: package_github.complete_package,
        PackageType.SwiftPkg: package_swift.complete_package,
    }

    try:
        if package.type in completion_map:
            package = completion_map[package.type](package)
            package.model_validate(
                cast(
                    dict[
                        str,
                        str
                        | Language
                        | list[str]
                        | list[Location]
                        | PackageType
                        | list[Advisory]
                        | list[Package]
                        | HealthMetadata
                        | bool
                        | object
                        | None,
                    ],
                    package.__dict__,
                ),
            )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package completion. Required fields are missing "
            "or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": package.locations,
                    "package_type": package.type,
                },
            },
        )
        return None

    return package
