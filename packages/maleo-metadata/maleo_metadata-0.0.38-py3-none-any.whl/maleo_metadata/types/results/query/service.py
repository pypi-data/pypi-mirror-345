from typing import Union
from maleo_metadata.models.transfers.results.query.service import MaleoMetadataServiceQueryResultsTransfers

class MaleoMetadataServiceQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataServiceQueryResultsTransfers.Fail,
        MaleoMetadataServiceQueryResultsTransfers.NoData,
        MaleoMetadataServiceQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataServiceQueryResultsTransfers.Fail,
        MaleoMetadataServiceQueryResultsTransfers.NoData,
        MaleoMetadataServiceQueryResultsTransfers.SingleData
    ]