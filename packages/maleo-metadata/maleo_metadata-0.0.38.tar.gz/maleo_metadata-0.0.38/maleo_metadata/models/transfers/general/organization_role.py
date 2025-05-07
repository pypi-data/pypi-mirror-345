from maleo_foundation.models.schemas.general import BaseGeneralSchemas
from maleo_metadata.models.schemas.organization_role import MaleoMetadataOrganizationRoleSchemas

class OrganizationRoleTransfers(
    MaleoMetadataOrganizationRoleSchemas.Name,
    MaleoMetadataOrganizationRoleSchemas.Key,
    BaseGeneralSchemas.Order,
    BaseGeneralSchemas.Status,
    BaseGeneralSchemas.Timestamps,
    BaseGeneralSchemas.Identifiers
):
    pass