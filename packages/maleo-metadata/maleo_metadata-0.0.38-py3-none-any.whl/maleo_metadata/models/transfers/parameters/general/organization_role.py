from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.parameters.general import BaseGeneralParametersTransfers
from maleo_metadata.enums.organization_role import MaleoMetadataOrganizationRoleEnums

class MaleoMetadataOrganizationRoleGeneralParametersTransfers:
    class GetSingleQuery(BaseGeneralParametersTransfers.GetSingleQuery): pass

    class GetSingle(BaseGeneralParametersTransfers.GetSingle):
        identifier:MaleoMetadataOrganizationRoleEnums.IdentifierType = Field(..., description="Identifier")