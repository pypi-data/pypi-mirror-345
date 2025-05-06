from enum import (
    Enum,
)

from labels.model.release import Release

PURL_QUALIFIER_DISTRO = "distro"


def purl_qualifiers(
    qualifiers: dict[str, str | None],
    release: Release | None = None,
) -> dict[str, str]:
    # Handling distro qualifiers
    if release:
        distro_qualifiers = []
        if release.id_:
            distro_qualifiers.append(release.id_)
        if release.version_id:
            distro_qualifiers.append(release.version_id)
        elif release.build_id:
            distro_qualifiers.append(release.build_id)

        if distro_qualifiers:
            qualifiers[PURL_QUALIFIER_DISTRO] = "-".join(distro_qualifiers)

    return {
        key: qualifiers.get(key, "") or ""
        for key in sorted(qualifiers.keys())
        if qualifiers.get(key)
    }


class Algorithm(Enum):
    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_256 = "sha3-256"
    SHA3_384 = "sha3-384"
    SHA3_512 = "sha3-512"
    BLAKE2B_256 = "blake2b-256"
    BLAKE2B_384 = "blake2b-384"
    BLAKE2B_512 = "blake2b-512"
    BLAKE3 = "blake3"
    MD2 = "md2"
    MD4 = "md4"
    MD5 = "md5"
    ADLER32 = "adler32"
    MD6 = "md6"


algorithm_length: dict[Algorithm, str] = {
    Algorithm.SHA1: "40",
    Algorithm.SHA224: "56",
    Algorithm.SHA256: "64",
    Algorithm.SHA384: "96",
    Algorithm.SHA512: "128",
    Algorithm.SHA3_256: "64",
    Algorithm.SHA3_384: "96",
    Algorithm.SHA3_512: "128",
    Algorithm.BLAKE2B_256: "64",
    Algorithm.BLAKE2B_384: "96",
    Algorithm.BLAKE2B_512: "128",
    Algorithm.BLAKE3: "256",
    Algorithm.MD2: "32",
    Algorithm.MD4: "32",
    Algorithm.MD5: "32",
    Algorithm.MD6: "512",
    Algorithm.ADLER32: "8",
}


def infer_algorithm(digest_value: str | None) -> str | None:
    if digest_value:
        for algorithm, length in algorithm_length.items():
            if len(digest_value) == int(length):
                return algorithm.value
    return None
