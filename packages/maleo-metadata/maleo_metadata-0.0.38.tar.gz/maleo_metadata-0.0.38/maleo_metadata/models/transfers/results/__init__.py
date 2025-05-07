from __future__ import annotations
from .general import MaleoMetadataGeneralResultsTransfers
from .query import MaleoMetadataQueryResultsTransfers

class MaleoMetadataResultsTransfers:
    General = MaleoMetadataGeneralResultsTransfers
    Query = MaleoMetadataQueryResultsTransfers