import json
import logging

from labels.advisories.database import BaseDatabase
from labels.advisories.match_versions import match_vulnerable_versions
from labels.advisories.utils import generate_cpe
from labels.model.advisories import Advisory

LOGGER = logging.getLogger(__name__)


class RootsDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(db_name="skims_sca_advisories.db")


DATABASE = RootsDatabase()


def get_package_advisories(
    package_manager: str,
    package_name: str,
    version: str,
) -> list[Advisory]:
    connection = DATABASE.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            adv_id,
            source,
            vulnerable_version,
            severity_level,
            severity,
            severity_v4,
            epss,
            details,
            percentile,
            cwe_ids,
            cve_finding,
            auto_approve
        FROM advisories
        WHERE package_manager = ? AND package_name = ?;
        """,
        (package_manager, package_name),
    )
    return [
        Advisory(
            id=result[0],
            urls=[result[1]],
            version_constraint=result[2] or None,
            severity=result[3],
            cvss3=result[4],
            cvss4=result[5],
            epss=result[6] or 0.0,
            description=result[7] or None,
            percentile=result[8] or 0.0,
            cpes=[generate_cpe(package_manager, package_name, version)],
            namespace=package_manager,
            cwe_ids=json.loads(result[9]) if result[9] else ["CWE-1395"],
            cve_finding=result[10],
            auto_approve=result[11] or False,
        )
        for result in cursor.fetchall()
    ]


def get_vulnerabilities(platform: str, product: str, version: str) -> list[Advisory]:
    vulnerabilities = []
    if (
        product
        and version
        and (advisories := get_package_advisories(platform, product.lower(), version))
    ):
        vulnerabilities = [
            advisor
            for advisor in advisories
            if match_vulnerable_versions(version.lower(), advisor.version_constraint)
        ]

    return vulnerabilities
