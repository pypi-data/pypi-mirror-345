from typing import Dict
from uuid import UUID
from maleo_metadata.enums.organization_role import MaleoMetadataOrganizationRoleEnums

class MaleoMetadataOrganizationRoleConstants:
    IDENTIFIER_TYPE_VALUE_TYPE_MAP:Dict[
        MaleoMetadataOrganizationRoleEnums.IdentifierType,
        object
    ] = {
        MaleoMetadataOrganizationRoleEnums.IdentifierType.ID: int,
        MaleoMetadataOrganizationRoleEnums.IdentifierType.UUID: UUID,
        MaleoMetadataOrganizationRoleEnums.IdentifierType.KEY: str,
        MaleoMetadataOrganizationRoleEnums.IdentifierType.NAME: str,
    }