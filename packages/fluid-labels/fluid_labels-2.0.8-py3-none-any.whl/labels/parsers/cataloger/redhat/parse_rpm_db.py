import logging
import os
from itertools import (
    zip_longest,
)
from typing import cast

from pydantic import (
    ValidationError,
)

from labels.model.file import (
    LocationReadCloser,
)
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
)
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.generic.parser import (
    Environment,
)
from labels.parsers.cataloger.redhat.package import (
    RpmDBEntry,
    RpmFileRecord,
    package_url,
)
from labels.parsers.cataloger.redhat.rpmdb import (
    open_db,
)
from labels.parsers.cataloger.redhat.rpmdb.package import (
    PackageInfo,
)
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def to_int(value: int | None, default: int = 0) -> int:
    return int(value) if isinstance(value, int) else default


def extract_rmp_file_records(resolver: Resolver, entry: PackageInfo) -> list[RpmFileRecord]:
    records: list[RpmFileRecord] = []
    file_attributes = cast(
        tuple[tuple[str, int, str, int, int, int, str, str], ...],
        zip_longest(
            entry.base_names,
            entry.dir_indexes,
            entry.file_digests,
            entry.file_flags,
            entry.file_modes,
            entry.file_sizes,
            entry.user_names,
            entry.group_names,
        ),
    )

    records.extend(
        record
        for attrs in file_attributes
        if (record := create_rpm_file_record(resolver, entry, attrs))
    )

    return records


def create_rpm_file_record(
    resolver: Resolver,
    entry: PackageInfo,
    attrs: tuple[str, int, str, int, int, int, str, str],
) -> RpmFileRecord | None:
    (
        base_name,
        dir_index,
        file_digest,
        file_flag,
        file_mode,
        file_size,
        file_username,
        file_groupname,
    ) = attrs

    if not base_name or not isinstance(dir_index, int):
        return None

    file_path = os.path.join(str(entry.dir_names[dir_index]), str(base_name))
    file_location = resolver.files_by_path(file_path)

    if not file_location:
        return None

    return RpmFileRecord(
        path=file_path,
        mode=to_int(file_mode, default=0),
        size=to_int(file_size, default=0),
        digest=Digest(
            algorithm="md5" if file_digest else None,
            value=str(file_digest) if file_digest else None,
        ),
        username=str(file_username),
        flags=str(file_flag),
        group_name=str(file_groupname) if file_groupname else None,
    )


def parse_rpm_db(
    resolver: Resolver,
    env: Environment,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    if not reader.location.coordinates:
        return packages, []
    database = open_db(reader.location.coordinates.real_path)
    if not database:
        return packages, []

    for entry in database.list_packages():
        name = entry.name
        version = entry.version

        if not name or not version:
            continue

        metadata = RpmDBEntry(
            id_="",
            name=name,
            version=version,
            epoch=entry.epoch,
            arch=entry.arch,
            release=entry.release,
            source_rpm=entry.source_rpm,
            vendor=entry.vendor,
            size=entry.size,
            modularitylabel=entry.modularity_label,
            files=extract_rmp_file_records(resolver, entry),
        )
        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[reader.location],
                    language=Language.UNKNOWN_LANGUAGE,
                    licenses=[entry.license],
                    type=PackageType.RpmPkg,
                    metadata=metadata,
                    p_url=package_url(
                        name=name,
                        arch=entry.arch,
                        epoch=entry.epoch,
                        source_rpm=entry.source_rpm,
                        version=version,
                        release=entry.release,
                        distro=env.linux_release,
                    ),
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": reader.location.path(),
                    },
                },
            )
            continue

    return packages, []
