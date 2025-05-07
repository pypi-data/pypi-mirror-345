from __future__ import annotations
from maleo_metadata.clients.controllers import MaleoMetadataControllers
from maleo_metadata.clients.services import MaleoMetadataServices
from maleo_metadata.clients.manager import MaleoMetadataClientManager

class MaleoMetadataClients:
    Controllers = MaleoMetadataControllers
    Services = MaleoMetadataServices
    Manager = MaleoMetadataClientManager