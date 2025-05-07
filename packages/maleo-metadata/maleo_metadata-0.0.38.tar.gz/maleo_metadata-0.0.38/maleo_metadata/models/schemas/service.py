from pydantic import Field
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.enums.service import MaleoMetadataServiceEnums

class MaleoMetadataServiceSchemas:
    class IdentifierType(BaseGeneralSchemas.IdentifierType):
        identifier:MaleoMetadataServiceEnums.IdentifierType = Field(..., description="Service's identifier type")

    class Key(BaseGeneralSchemas.Key):
        key:str = Field(..., max_length=20, description="Service's key")

    class Name(BaseGeneralSchemas.Name):
        name:str = Field(..., max_length=20, description="Service's name")