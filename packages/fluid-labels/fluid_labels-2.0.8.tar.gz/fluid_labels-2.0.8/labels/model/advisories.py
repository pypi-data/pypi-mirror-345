from pydantic import BaseModel, Field, field_validator


class Advisory(BaseModel):
    cpes: list[str]
    description: str | None = Field(min_length=1)
    epss: float
    id: str = Field(min_length=1)
    namespace: str = Field(min_length=1)
    percentile: float
    severity: str = Field(min_length=1)
    urls: list[str]
    version_constraint: str | None = Field()
    cvss3: str | None = Field()
    cvss4: str | None = Field()
    cwe_ids: list[str] | None = None
    cve_finding: str | None = None
    auto_approve: bool = False

    @field_validator("cpes")
    @classmethod
    def check_cpes_min_length(cls, value: list[str]) -> list[str]:
        for cpe in value:
            if len(cpe) < 1:
                error_message = "Each cpe string must be at least 1 character long."
                raise ValueError(error_message)
        return value

    @field_validator("urls")
    @classmethod
    def check_urls_min_length(cls, value: list[str]) -> list[str]:
        for url in value:
            if len(url) < 1:
                error_message = "Each url string must be at least 1 character long."
                raise ValueError(error_message)
        return value

    def get_info_count(self) -> int:
        info_count = 0
        for attr in [
            self.cpes,
            self.description,
            self.urls,
            self.version_constraint,
        ]:
            if attr:
                info_count += 1
        return info_count

    def __repr__(self) -> str:
        return f"Advisory(id={self.id}, namespace={self.namespace}, severity={self.severity})"
