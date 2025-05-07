from __future__ import annotations
from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_foundation.models.transfers.results.service.query import BaseServiceQueryResultsTransfers
from maleo_metadata.models.schemas.system_role import MaleoMetadataSystemRoleSchemas

class MaleoMetadataSystemRoleQueryResultsTransfers:
    class Row(
        MaleoMetadataSystemRoleSchemas.Name,
        MaleoMetadataSystemRoleSchemas.Key,
        BaseGeneralSchemas.Order,
        BaseServiceQueryResultsTransfers.Row
    ): pass

    class Fail(BaseServiceQueryResultsTransfers.Fail): pass

    class NoData(BaseServiceQueryResultsTransfers.NoData): pass

    class SingleData(BaseServiceQueryResultsTransfers.SingleData):
        data:MaleoMetadataSystemRoleQueryResultsTransfers.Row

    class MultipleData(BaseServiceQueryResultsTransfers.UnpaginatedMultipleData):
        data:list[MaleoMetadataSystemRoleQueryResultsTransfers.Row]