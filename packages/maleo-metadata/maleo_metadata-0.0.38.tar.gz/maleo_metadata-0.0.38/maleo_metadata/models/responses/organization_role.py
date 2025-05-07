from pydantic import Field
from maleo_foundation.models.responses import BaseResponses
from maleo_metadata.enums.organization_role import MaleoMetadataOrganizationRoleEnums
from maleo_metadata.models.transfers.general.organization_role import OrganizationRoleTransfers

class MaleoMetadataOrganizationRoleResponses:
    class InvalidIdentifierRole(BaseResponses.BadRequest):
        code:str = "MDT-OGR-001"
        message:str = "Invalid identifier type"
        description:str = "Invalid identifier type is given in the request"
        other: str = f"Valid identifier roles: {[f'{e.name} ({e.value})' for e in MaleoMetadataOrganizationRoleEnums.IdentifierType]}"

    class InvalidValueRole(BaseResponses.BadRequest):
        code:str = "MDT-OGR-002"
        message:str = "Invalid value type"
        description:str = "Invalid value type is given in the request"

    class GetSingle(BaseResponses.SingleData):
        code:str = "MDT-OGR-003"
        message:str = "Organization role found"
        description:str = "Requested organization role found in database"
        data:OrganizationRoleTransfers = Field(..., description="Organization role")

    class GetMultiple(BaseResponses.UnpaginatedMultipleData):
        code:str = "MDT-OGR-004"
        message:str = "Organization roles found"
        description:str = "Requested organization roles found in database"
        data:list[OrganizationRoleTransfers] = Field(..., description="Organization roles")