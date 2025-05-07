from typing import Union
from maleo_metadata.models.transfers.results.general.organization_role import MaleoMetadataOrganizationRoleGeneralResultsTransfers

class MaleoMetadataOrganizationRoleGeneralResultsTypes:
    GetMultiple = Union[
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail,
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.NoData,
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail,
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.NoData,
        MaleoMetadataOrganizationRoleGeneralResultsTransfers.SingleData
    ]