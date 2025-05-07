from typing import List, Optional
from maleo_metadata.enums.gender import MaleoMetadataGenderEnums
from maleo_metadata.models.transfers.general.gender import GenderTransfers

class MaleoMetadataGenderGeneralTypes:
    #* Simple blood type
    SimpleGender = MaleoMetadataGenderEnums.Gender
    OptionalSimpleGender = Optional[SimpleGender]
    ListOfSimpleGender = List[SimpleGender]
    OptionalListOfSimpleGender = Optional[List[SimpleGender]]

    #* Expanded blood type
    ExpandedGender = GenderTransfers
    OptionalExpandedGender = Optional[ExpandedGender]
    ListOfExpandedGender = List[ExpandedGender]
    OptionalListOfExpandedGender = Optional[List[ExpandedGender]]