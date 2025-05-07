from typing import Union
from maleo_metadata.models.transfers.results.query.blood_type import MaleoMetadataBloodTypeQueryResultsTransfers

class MaleoMetadataBloodTypeQueryResultsTypes:
    GetMultiple = Union[
        MaleoMetadataBloodTypeQueryResultsTransfers.Fail,
        MaleoMetadataBloodTypeQueryResultsTransfers.NoData,
        MaleoMetadataBloodTypeQueryResultsTransfers.MultipleData
    ]

    GetSingle = Union[
        MaleoMetadataBloodTypeQueryResultsTransfers.Fail,
        MaleoMetadataBloodTypeQueryResultsTransfers.NoData,
        MaleoMetadataBloodTypeQueryResultsTransfers.SingleData
    ]