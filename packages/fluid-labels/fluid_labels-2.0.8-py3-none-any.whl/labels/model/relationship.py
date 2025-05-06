from enum import Enum

from pydantic import BaseModel, ConfigDict

from labels.model.package import Package


class RelationshipType(Enum):
    OWNERSHIP_BY_FILE_OVERLAP_RELATIONSHIP = "ownership-by-file-overlap"
    EVIDENT_BY_RELATIONSHIP = "evident-by"
    CONTAINS_RELATIONSHIP = "contains"
    DEPENDENCY_OF_RELATIONSHIP = "dependency-of"
    DESCRIBED_BY_RELATIONSHIP = "described-by"


class Relationship(BaseModel):
    from_: Package
    to_: Package
    type: RelationshipType
    model_config = ConfigDict(frozen=True)
