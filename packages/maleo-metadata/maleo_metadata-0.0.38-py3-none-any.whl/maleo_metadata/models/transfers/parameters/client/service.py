from __future__ import annotations
from maleo_foundation.models.transfers.parameters.client import BaseClientParametersTransfers

class MaleoMetadataServiceClientParametersTransfers:
    class GetMultiple(BaseClientParametersTransfers.GetUnpaginatedMultiple): pass
    class GetMultipleQuery(BaseClientParametersTransfers.GetUnpaginatedMultipleQuery): pass