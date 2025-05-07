from typing import List, Optional
from maleo_metadata.enums.system_role import MaleoMetadataSystemRoleEnums
from maleo_metadata.models.transfers.general.system_role import SystemRoleTransfers

class MaleoMetadataSystemRoleGeneralTypes:
    #* Simple system type
    SimpleSystemRole = MaleoMetadataSystemRoleEnums.SystemRole
    OptionalSimpleSystemRole = Optional[SimpleSystemRole]
    ListOfSimpleSystemRole = List[SimpleSystemRole]
    OptionalListOfSimpleSystemRole = Optional[List[SimpleSystemRole]]

    #* Expanded system type
    ExpandedSystemRole = SystemRoleTransfers
    OptionalExpandedSystemRole = Optional[ExpandedSystemRole]
    ListOfExpandedSystemRole = List[ExpandedSystemRole]
    OptionalListOfExpandedSystemRole = Optional[List[ExpandedSystemRole]]