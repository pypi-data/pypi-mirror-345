from typing import Union
from maleo_metadata.models.transfers.results.query.organization_type import MaleoMetadataOrganizationTypeQueryResultsTransfers

class MaleoMetadataOrganizationTypeQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataOrganizationTypeQueryResultsTransfers.Fail,
        MaleoMetadataOrganizationTypeQueryResultsTransfers.NoData,
        MaleoMetadataOrganizationTypeQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataOrganizationTypeQueryResultsTransfers.Fail,
        MaleoMetadataOrganizationTypeQueryResultsTransfers.NoData,
        MaleoMetadataOrganizationTypeQueryResultsTransfers.SingleData
    ]