from typing import Union
from maleo_metadata.models.transfers.results.query.system_role import MaleoMetadataSystemRoleQueryResultsTransfers

class MaleoMetadataSystemRoleQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataSystemRoleQueryResultsTransfers.Fail,
        MaleoMetadataSystemRoleQueryResultsTransfers.NoData,
        MaleoMetadataSystemRoleQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataSystemRoleQueryResultsTransfers.Fail,
        MaleoMetadataSystemRoleQueryResultsTransfers.NoData,
        MaleoMetadataSystemRoleQueryResultsTransfers.SingleData
    ]