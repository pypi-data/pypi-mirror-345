from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from labels.model.file import LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Release
from labels.model.resolver import Resolver


class Environment(BaseModel):
    linux_release: Release | None
    model_config = ConfigDict(frozen=True)


Parser = Callable[
    [Resolver, Environment, LocationReadCloser],
    tuple[list[Package], list[Relationship]] | None,
]
