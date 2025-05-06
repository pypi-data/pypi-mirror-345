from typing import cast

import os_release
from os_release.parser import OsReleaseParseException

from labels.model.release import OsReleaseDict, Release
from labels.model.resolver import Resolver


def identify_release(resolver: Resolver) -> Release | None:
    possible_files = [
        "/etc/os-release",
        "/usr/lib/os-release",
        "/etc/system-release-cpe",
        "/etc/redhat-release",
        "/bin/busybox",
    ]

    for file in possible_files:
        if not resolver.has_path(file):
            continue
        location = resolver.files_by_path(file)[0]
        content_reader = resolver.file_contents_by_location(location)
        if not content_reader:
            continue
        content = content_reader.read()
        release = parse_os_release(content)
        if release:
            return release
    return None


def parse_os_release(content: str) -> Release | None:
    try:
        release: OsReleaseDict | None = os_release.parse_str(content)
    except OsReleaseParseException:
        release = _force_parse(content)
    if release:
        id_like: list[str] = []
        if "ID_LIKE" in release:
            id_like = sorted(release["ID_LIKE"].split(" "))
        return Release(
            pretty_name=release.get("PRETTY_NAME", ""),
            name=release.get("NAME", ""),
            id_=release.get("ID", ""),
            id_like=id_like,
            version=release.get("VERSION", ""),
            version_id=release.get("VERSION_ID", ""),
            version_code_name=release.get("VERSION_CODENAME", ""),
            build_id=release.get("BUILD_ID", ""),
            image_id=release.get("IMAGE_ID", ""),
            image_version=release.get("IMAGE_VERSION", ""),
            variant=release.get("VARIANT", ""),
            variant_id=release.get("VARIANT_ID", ""),
            home_url=release.get("HOME_URL", ""),
            support_url=release.get("SUPPORT_URL", ""),
            bug_report_url=release.get("BUG_REPORT_URL", ""),
            privacy_policy_url=release.get("PRIVACY_POLICY_URL", ""),
            cpe_name=release.get("CPE_NAME", ""),
            support_end=release.get("SUPPORT_END", ""),
        )
    return None


def _is_valid_key(key: str) -> bool:
    return key.isidentifier() and key.isupper()


def _force_parse(content: str) -> OsReleaseDict | None:
    lines: list[tuple[str, str]] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip("\"'")

        if not _is_valid_key(key):
            continue

        lines.append((key, value))

    if not lines:
        return None
    return cast(OsReleaseDict, dict(lines))
