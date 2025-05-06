import re
from typing import TextIO, cast


def parse_licenses_from_copyright(reader: TextIO) -> list[str]:
    result = []
    for raw_line in reader:
        line = raw_line.rstrip("\n")
        if value := find_license_clause(r"^License: (?P<license>\S*)", "license", line):
            result.append(value)
        if value := find_license_clause(
            r"/usr/share/common-licenses/(?P<license>[0-9A-Za-z_.\-]+)",
            "license",
            line,
        ):
            result.append(value)

    return list(set(result))


def find_license_clause(pattern: str, value_group: str, line: str) -> str | None:
    match = re.search(pattern, line)
    if match:
        return ensure_is_single_license(cast(str, match.group(value_group)))
    return None


def ensure_is_single_license(candidate: str) -> str | None:
    candidate = candidate.strip()
    if " or " in candidate or " and " in candidate:
        # This is a multi-license summary, ignore this.
        return None
    if candidate and candidate.lower() != "none":
        # The license may be at the end of a sentence; clean '.' characters.
        return candidate.rstrip(".")
    return None
