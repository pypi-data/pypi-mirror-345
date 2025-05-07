from __future__ import annotations
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.models.transfers.results.service.query import BaseServiceQueryResultsTransfers
from maleo_metadata.models.schemas.gender import MaleoMetadataGenderSchemas

class MaleoMetadataGenderQueryResultsTransfers:
    class Row(
        MaleoMetadataGenderSchemas.Name,
        MaleoMetadataGenderSchemas.Key,
        BaseGeneralSchemas.Order,
        BaseServiceQueryResultsTransfers.Row
    ): pass

    class Fail(BaseServiceQueryResultsTransfers.Fail): pass

    class NoData(BaseServiceQueryResultsTransfers.NoData): pass

    class SingleData(BaseServiceQueryResultsTransfers.SingleData):
        data:MaleoMetadataGenderQueryResultsTransfers.Row

    class MultipleData(BaseServiceQueryResultsTransfers.UnpaginatedMultipleData):
        data:list[MaleoMetadataGenderQueryResultsTransfers.Row]