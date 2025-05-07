from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo

from pyeudiw.federation.schemas.federation_entity import FederationEntity
from pyeudiw.federation.schemas.openid_credential_verifier import (
    OpenIDCredentialVerifier,
)
from pyeudiw.jwk.schemas.public import JwksSchema
from pyeudiw.tools.schema_utils import check_algorithm


class EntityConfigurationHeader(BaseModel):
    alg: str
    kid: str
    typ: Literal["entity-statement+jwt"]

    @field_validator("alg")
    @classmethod
    def _check_alg(cls, alg, info: ValidationInfo):
        return check_algorithm(alg, info)


class EntityConfigurationMetadataSchema(BaseModel):
    openid_credential_verifier: OpenIDCredentialVerifier
    federation_entity: FederationEntity


class EntityConfigurationPayload(BaseModel):
    iat: int
    exp: int
    iss: HttpUrl
    sub: HttpUrl
    jwks: JwksSchema
    metadata: EntityConfigurationMetadataSchema
    authority_hints: List[HttpUrl]


class EntityStatementPayload(BaseModel, extra="forbid"):
    exp: int
    iat: int
    iss: HttpUrl
    sub: HttpUrl
    jwks: JwksSchema
    source_endpoint: Optional[str] = None
    metadata_policy: Optional[dict] = None
    metadata: Optional[dict] = None
    trust_marks: Optional[list] = None
