from __future__ import annotations
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.models.transfers.results.service.query import BaseServiceQueryResultsTransfers
from maleo_metadata.models.schemas.user_type import MaleoMetadataUserTypeSchemas

class MaleoMetadataUserTypeQueryResultsTransfers:
    class Row(
        MaleoMetadataUserTypeSchemas.Name,
        MaleoMetadataUserTypeSchemas.Key,
        BaseGeneralSchemas.Order,
        BaseServiceQueryResultsTransfers.Row
    ): pass

    class Fail(BaseServiceQueryResultsTransfers.Fail): pass

    class NoData(BaseServiceQueryResultsTransfers.NoData): pass

    class SingleData(BaseServiceQueryResultsTransfers.SingleData):
        data:MaleoMetadataUserTypeQueryResultsTransfers.Row

    class MultipleData(BaseServiceQueryResultsTransfers.UnpaginatedMultipleData):
        data:list[MaleoMetadataUserTypeQueryResultsTransfers.Row]