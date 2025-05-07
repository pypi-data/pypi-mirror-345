from __future__ import annotations
from maleo_foundation.models.transfers.parameters.service import BaseServiceParametersTransfers

class MaleoMetadataGenderServiceParametersTransfers:
    class GetMultipleQuery(BaseServiceParametersTransfers.GetUnpaginatedMultipleQuery): pass
    class GetMultiple(BaseServiceParametersTransfers.GetUnpaginatedMultiple): pass