from typing import Union
from maleo_metadata.models.transfers.results.query.user_type import MaleoMetadataUserTypeQueryResultsTransfers

class MaleoMetadataUserTypeQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataUserTypeQueryResultsTransfers.Fail,
        MaleoMetadataUserTypeQueryResultsTransfers.NoData,
        MaleoMetadataUserTypeQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataUserTypeQueryResultsTransfers.Fail,
        MaleoMetadataUserTypeQueryResultsTransfers.NoData,
        MaleoMetadataUserTypeQueryResultsTransfers.SingleData
    ]