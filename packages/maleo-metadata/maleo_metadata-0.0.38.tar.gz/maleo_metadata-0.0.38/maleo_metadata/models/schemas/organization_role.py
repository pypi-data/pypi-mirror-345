from pydantic import Field
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.enums.organization_role import MaleoMetadataOrganizationRoleEnums

class MaleoMetadataOrganizationRoleSchemas:
    class IdentifierType(BaseGeneralSchemas.IdentifierType):
        identifier:MaleoMetadataOrganizationRoleEnums.IdentifierType = Field(..., description="Organization Role's identifier type")

    class Key(BaseGeneralSchemas.Key):
        key:str = Field(..., max_length=20, description="Organization Role's key")

    class Name(BaseGeneralSchemas.Name):
        name:str = Field(..., max_length=20, description="Organization Role's name")