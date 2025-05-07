from typing import List, Optional
from maleo_metadata.enums.organization_type import MaleoMetadataOrganizationTypeEnums
from maleo_metadata.models.transfers.general.organization_type import OrganizationTypeTransfers

class MaleoMetadataOrganizationTypeGeneralTypes:
    #* Simple organization type
    SimpleOrganizationType = MaleoMetadataOrganizationTypeEnums.OrganizationType
    OptionalSimpleOrganizationType = Optional[SimpleOrganizationType]
    ListOfSimpleOrganizationType = List[SimpleOrganizationType]
    OptionalListOfSimpleOrganizationType = Optional[List[SimpleOrganizationType]]

    #* Expanded organization type
    ExpandedOrganizationType = OrganizationTypeTransfers
    OptionalExpandedOrganizationType = Optional[ExpandedOrganizationType]
    ListOfExpandedOrganizationType = List[ExpandedOrganizationType]
    OptionalListOfExpandedOrganizationType = Optional[List[ExpandedOrganizationType]]