import hashlib
import json
from datetime import datetime
from enum import Enum, StrEnum

from pydantic import BaseModel, Field, field_validator

from labels.model.advisories import Advisory
from labels.model.file import Location


class Platform(StrEnum):
    CARGO = "CARGO"
    COMPOSER = "COMPOSER"
    CONAN = "CONAN"
    ERLANG = "ERLANG"
    GEM = "GEM"
    GITHUB_ACTIONS = "GITHUB_ACTIONS"
    GO = "GO"
    MAVEN = "MAVEN"
    NPM = "NPM"
    NUGET = "NUGET"
    PIP = "PIP"
    PUB = "PUB"
    SWIFT = "SWIFT"
    CABAL = "CABAL"
    CRAN = "CRAN"


class Language(StrEnum):
    UNKNOWN_LANGUAGE = "unknown_language"
    CPP = "c++"
    DART = "dart"
    DOTNET = "dotnet"
    ELIXIR = "elixir"
    ERLANG = "erlang"
    GO = "go"
    GITHUB_ACTIONS = "github_actions"
    HASKELL = "haskell"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    PHP = "php"
    PYTHON = "python"
    R = "R"
    RUBY = "ruby"
    RUST = "rust"
    SWIFT = "swift"

    def get_platform_value(self) -> str | None:
        language_to_platform = {
            Language.CPP: Platform.CONAN.value,
            Language.DART: Platform.PUB.value,
            Language.DOTNET: Platform.NUGET.value,
            Language.ELIXIR: Platform.ERLANG.value,
            Language.ERLANG: Platform.ERLANG.value,
            Language.GO: Platform.GO.value,
            Language.HASKELL: Platform.CABAL.value,
            Language.JAVA: Platform.MAVEN.value,
            Language.JAVASCRIPT: Platform.NPM.value,
            Language.PHP: Platform.COMPOSER.value,
            Language.PYTHON: Platform.PIP.value,
            Language.R: Platform.CRAN.value,
            Language.RUBY: Platform.GEM.value,
            Language.RUST: Platform.CARGO.value,
            Language.SWIFT: Platform.SWIFT.value,
            Language.GITHUB_ACTIONS: Platform.GITHUB_ACTIONS.value,
            Language.UNKNOWN_LANGUAGE: None,
        }
        return language_to_platform.get(self)


class PackageType(Enum):
    UnknownPkg = "UnknownPackage"
    AlpmPkg = "alpm"
    ApkPkg = "apk"
    BinaryPkg = "binary"
    CocoapodsPkg = "pod"
    ConanPkg = "conan"
    DartPubPkg = "dart-pub"
    DebPkg = "deb"
    DotnetPkg = "dotnet"
    ErlangOTPPkg = "erlang-otp"
    GemPkg = "gem"
    GithubActionPkg = "github-action"
    GithubActionWorkflowPkg = "github-action-workflow"
    GoModulePkg = "go-module"
    GraalVMNativeImagePkg = "graalvm-native-image"
    HackagePkg = "hackage"
    HexPkg = "hex"
    JavaPkg = "java-archive"
    JenkinsPluginPkg = "jenkins-plugin"
    KbPkg = "msrc-kb"
    LinuxKernelPkg = "linux-kernel"
    LinuxKernelModulePkg = "linux-kernel-module"
    NixPkg = "nix"
    NpmPkg = "npm"
    PhpComposerPkg = "php-composer"
    PhpPeclPkg = "php-pecl-pkg"
    PortagePkg = "portage"
    PythonPkg = "python"
    Rpkg = "R-package"
    RpmPkg = "rpm"
    RustPkg = "rust-crate"
    SwiftPkg = "swift"
    WordpressPluginPkg = "wordpress-plugin"


class Digest(BaseModel):
    algorithm: str | None = Field(min_length=1)
    value: str | None = Field(min_length=1)


class Artifact(BaseModel):
    url: str = Field(min_length=1)
    integrity: Digest | None = None


class HealthMetadata(BaseModel):
    latest_version: str | None = Field(default=None, min_length=1)
    latest_version_created_at: str | datetime | None = None
    artifact: Artifact | None = None
    authors: str | None = Field(default=None, min_length=1)

    @field_validator("latest_version_created_at", mode="before")
    @classmethod
    def validate_latest_version_created_at(
        cls,
        value: str | datetime | None,
    ) -> str | datetime | None:
        if isinstance(value, str) and len(value) < 1:
            error_message = (
                "latest_version_created_at must be at least 1 character long when it is a string."
            )
            raise ValueError(error_message)
        return value


class Package(BaseModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    language: Language
    licenses: list[str]
    locations: list[Location]
    type: PackageType
    advisories: list[Advisory] | None = None
    dependencies: list["Package"] | None = None
    found_by: str | None = Field(default=None, min_length=1)
    health_metadata: HealthMetadata | None = None
    is_dev: bool = False
    metadata: object | None = None
    p_url: str = Field(min_length=1)

    @property
    def id_(self) -> str:
        return self.id_by_hash()

    def id_by_hash(self) -> str:
        try:
            obj_data = {
                "name": self.name,
                "version": self.version,
                "language": self.language.value,
                "type": self.type.value,
                "p_url": self.p_url,
            }
            obj_str = json.dumps(obj_data, sort_keys=True)
            return hashlib.sha256(obj_str.encode()).hexdigest()
        except Exception as exc:  # noqa: BLE001
            return f"Could not build ID for object={self}: {exc}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Package):
            return False

        return (
            self.name == other.name
            and self.version == other.version
            and self.language == other.language
            and self.licenses == other.licenses
            and self.locations == other.locations
            and self.type == other.type
            and self.advisories == other.advisories
            and self.dependencies == other.dependencies
            and self.found_by == other.found_by
            and self.health_metadata == other.health_metadata
            and self.is_dev == other.is_dev
            and self.metadata == other.metadata
            and self.p_url == other.p_url
        )

    def __hash__(self) -> int:
        return hash(self.id_)

    @field_validator("licenses")
    @classmethod
    def check_licenses_min_length(cls, value: list[str]) -> list[str]:
        for license_str in value:
            if len(license_str) < 1:
                error_message = "Each license string must be at least 1 character long."
                raise ValueError(error_message)
        return value
