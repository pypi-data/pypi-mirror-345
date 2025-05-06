from urllib.parse import parse_qs


def extract_distro_info(pkg_str: str) -> tuple[str | None, str | None, str | None]:
    parts = pkg_str.split("?", 1)
    if len(parts) != 2:
        return None, None, None

    query = parts[1]
    params = parse_qs(query)
    distro_id = params.get("distro_id", [None])[0]
    distro_version = params.get("distro_version_id", [None])[0]
    arch = params.get("arch", [None])[0]
    return distro_id, distro_version, arch
