from typing import Union
from maleo_metadata.models.transfers.results.query.gender import MaleoMetadataGenderQueryResultsTransfers

class MaleoMetadataGenderQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataGenderQueryResultsTransfers.Fail,
        MaleoMetadataGenderQueryResultsTransfers.NoData,
        MaleoMetadataGenderQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataGenderQueryResultsTransfers.Fail,
        MaleoMetadataGenderQueryResultsTransfers.NoData,
        MaleoMetadataGenderQueryResultsTransfers.SingleData
    ]