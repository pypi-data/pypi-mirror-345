from __future__ import annotations
from pydantic import Field
from maleo_foundation.models.transfers.results.service.general import BaseServiceGeneralResultsTransfers
from maleo_metadata.models.transfers.general.organization_role import OrganizationRoleTransfers

class MaleoMetadataOrganizationRoleGeneralResultsTransfers:
    class Fail(BaseServiceGeneralResultsTransfers.Fail): pass

    class NoData(BaseServiceGeneralResultsTransfers.NoData): pass

    class SingleData(BaseServiceGeneralResultsTransfers.SingleData):
        data:OrganizationRoleTransfers = Field(..., description="Single organization role data")

    class MultipleData(BaseServiceGeneralResultsTransfers.UnpaginatedMultipleData):
        data:list[OrganizationRoleTransfers] = Field(..., description="Multiple organization roles data")