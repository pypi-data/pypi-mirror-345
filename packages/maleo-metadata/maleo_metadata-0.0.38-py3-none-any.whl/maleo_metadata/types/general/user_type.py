from typing import List, Optional
from maleo_metadata.enums.user_type import MaleoMetadataUserTypeEnums
from maleo_metadata.models.transfers.general.user_type import UserTypeTransfers

class MaleoMetadataUserTypeGeneralTypes:
    #* Simple user type
    SimpleUserType = MaleoMetadataUserTypeEnums.UserType
    OptionalSimpleUserType = Optional[SimpleUserType]
    ListOfSimpleUserType = List[SimpleUserType]
    OptionalListOfSimpleUserType = Optional[List[SimpleUserType]]

    #* Expanded user type
    ExpandedUserType = UserTypeTransfers
    OptionalExpandedUserType = Optional[ExpandedUserType]
    ListOfExpandedUserType = List[ExpandedUserType]
    OptionalListOfExpandedUserType = Optional[List[ExpandedUserType]]