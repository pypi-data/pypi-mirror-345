import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

from spdx_tools.spdx.model.document import Document
from spdx_tools.spdx.model.package import Package as SPDX_Package
from spdx_tools.spdx.model.package import PackagePurpose
from spdx_tools.spdx.model.relationship import Relationship as SPDXRelationship
from spdx_tools.spdx.model.relationship import RelationshipType as SPDXRelationshipType

from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.output.spdx.complete_file import (
    NOASSERTION,
    add_authors,
    add_external_refs,
    add_integrity,
    add_license,
    get_spdx_id,
)

LOGGER = logging.getLogger(__name__)


def package_to_spdx_pkg(package: Package) -> SPDX_Package:
    spdx_id = get_spdx_id(package)
    license_declared = add_license(package.licenses)
    originator = add_authors(package.health_metadata)
    external_refs = add_external_refs(package)
    checksums = add_integrity(package.health_metadata)

    return SPDX_Package(
        spdx_id=spdx_id,
        name=package.name,
        download_location=NOASSERTION,
        version=package.version,
        license_declared=license_declared,
        originator=originator,
        primary_package_purpose=PackagePurpose.LIBRARY,
        external_references=external_refs,
        checksums=checksums,
    )


def create_package_cache(packages: list[Package]) -> dict[Package, SPDX_Package]:
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        return dict(zip(packages, executor.map(package_to_spdx_pkg, packages), strict=False))


def create_document_relationships(
    document: Document,
    spdx_packages: list[SPDX_Package],
) -> list[SPDXRelationship]:
    doc_spdx_id = document.creation_info.spdx_id
    return [
        SPDXRelationship(doc_spdx_id, SPDXRelationshipType.DESCRIBES, pkg.spdx_id)
        for pkg in spdx_packages
    ]


def process_relationship(
    relationship: Relationship,
    spdx_id_cache: dict[Package, str],
) -> SPDXRelationship | None:
    to_pkg = relationship.to_
    from_pkg = relationship.from_

    to_pkg_id = spdx_id_cache.get(to_pkg)
    from_pkg_id = spdx_id_cache.get(from_pkg)

    if to_pkg_id and from_pkg_id:
        return SPDXRelationship(to_pkg_id, SPDXRelationshipType.DEPENDENCY_OF, from_pkg_id)

    return None


def process_relationships(
    document: Document,
    relationships: list[Relationship],
    spdx_id_cache: dict[Package, str],
    document_relationships: list[SPDXRelationship],
) -> None:
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        relationship_results = filter(
            None,
            executor.map(
                lambda r: process_relationship(r, spdx_id_cache),
                relationships,
            ),
        )
        document_relationships.extend(relationship_results)

    document.relationships = document_relationships


def add_packages_and_relationships(
    document: Document,
    packages: list[Package],
    relationships: list[Relationship],
) -> None:
    package_cache = create_package_cache(packages)

    spdx_id_cache = {pkg: spdx_pkg.spdx_id for pkg, spdx_pkg in package_cache.items()}

    document.packages = list(package_cache.values())

    document_relationships = create_document_relationships(document, document.packages)

    process_relationships(document, relationships, spdx_id_cache, document_relationships)
