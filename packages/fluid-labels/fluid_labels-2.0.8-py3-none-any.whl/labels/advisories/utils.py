def generate_cpe(package_manager: str, package_name: str, vulnerable_version: str) -> str:
    part = "a"
    vendor = package_name.split(":")[0] if ":" in package_name else "*"
    product = package_name.lower()
    version = vulnerable_version
    language = package_manager
    update = edition = sw_edition = target_sw = target_hw = other = "*"

    return (
        f"cpe:2.3:{part}:{vendor}:{product}:{version}:{update}:{edition}:"
        f"{language}:{sw_edition}:{target_sw}:{target_hw}:{other}"
    )
