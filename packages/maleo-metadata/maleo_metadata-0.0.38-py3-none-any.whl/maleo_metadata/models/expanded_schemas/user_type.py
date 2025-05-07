from pydantic import BaseModel, Field
from maleo_metadata.types.general.user_type import MaleoMetadataUserTypeGeneralTypes

class MaleoMetadataUserTypeExpandedSchemas:
    class SimpleUserType(BaseModel):
        user_type:MaleoMetadataUserTypeGeneralTypes.SimpleUserType = Field(..., description="User type")

    class OptionalSimpleUserType(BaseModel):
        user_type:MaleoMetadataUserTypeGeneralTypes.OptionalSimpleUserType = Field(None, description="User type")

    class ListOfSimpleUserType(BaseModel):
        user_types:MaleoMetadataUserTypeGeneralTypes.ListOfSimpleUserType = Field([], description="User types")

    class OptionalListOfSimpleUserType(BaseModel):
        user_types:MaleoMetadataUserTypeGeneralTypes.OptionalListOfSimpleUserType = Field(None, description="User types")

    class ExpandedUserType(BaseModel):
        user_type_details:MaleoMetadataUserTypeGeneralTypes.ExpandedUserType = Field(..., description="User type's details")

    class OptionalExpandedUserType(BaseModel):
        user_type_details:MaleoMetadataUserTypeGeneralTypes.OptionalExpandedUserType = Field(None, description="User type's details")

    class ListOfExpandedUserType(BaseModel):
        user_types_details:MaleoMetadataUserTypeGeneralTypes.ListOfExpandedUserType = Field([], description="User types's details")

    class OptionalListOfExpandedUserType(BaseModel):
        user_types_details:MaleoMetadataUserTypeGeneralTypes.OptionalListOfExpandedUserType = Field(None, description="User types's details")