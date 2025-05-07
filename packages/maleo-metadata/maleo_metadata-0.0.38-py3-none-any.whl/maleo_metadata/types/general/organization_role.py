from typing import List, Optional
from maleo_metadata.enums.organization_role import MaleoMetadataOrganizationRoleEnums
from maleo_metadata.models.transfers.general.organization_role import OrganizationRoleTransfers

class MaleoMetadataOrganizationRoleGeneralTypes:
    #* Simple organization type
    SimpleOrganizationRole = MaleoMetadataOrganizationRoleEnums.OrganizationRole
    OptionalSimpleOrganizationRole = Optional[SimpleOrganizationRole]
    ListOfSimpleOrganizationRole = List[SimpleOrganizationRole]
    OptionalListOfSimpleOrganizationRole = Optional[List[SimpleOrganizationRole]]

    #* Expanded organization type
    ExpandedOrganizationRole = OrganizationRoleTransfers
    OptionalExpandedOrganizationRole = Optional[ExpandedOrganizationRole]
    ListOfExpandedOrganizationRole = List[ExpandedOrganizationRole]
    OptionalListOfExpandedOrganizationRole = Optional[List[ExpandedOrganizationRole]]