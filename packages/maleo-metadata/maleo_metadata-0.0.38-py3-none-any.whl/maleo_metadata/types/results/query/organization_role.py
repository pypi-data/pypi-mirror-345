from typing import Union
from maleo_metadata.models.transfers.results.query.organization_role import MaleoMetadataOrganizationRoleQueryResultsTransfers

class MaleoMetadataOrganizationRoleQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataOrganizationRoleQueryResultsTransfers.Fail,
        MaleoMetadataOrganizationRoleQueryResultsTransfers.NoData,
        MaleoMetadataOrganizationRoleQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataOrganizationRoleQueryResultsTransfers.Fail,
        MaleoMetadataOrganizationRoleQueryResultsTransfers.NoData,
        MaleoMetadataOrganizationRoleQueryResultsTransfers.SingleData
    ]