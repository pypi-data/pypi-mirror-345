from pydantic import BaseModel, Field
from maleo_metadata.types.general.blood_type import MaleoMetadataBloodTypeGeneralTypes

class MaleoMetadataBloodTypeExpandedSchemas:
    class SimpleBloodType(BaseModel):
        blood_type:MaleoMetadataBloodTypeGeneralTypes.SimpleBloodType = Field(..., description="Blood type")

    class OptionalSimpleBloodType(BaseModel):
        blood_type:MaleoMetadataBloodTypeGeneralTypes.OptionalSimpleBloodType = Field(None, description="Blood type")

    class ListOfSimpleBloodType(BaseModel):
        blood_types:MaleoMetadataBloodTypeGeneralTypes.ListOfSimpleBloodType = Field([], description="Blood types")

    class OptionalListOfSimpleBloodType(BaseModel):
        blood_types:MaleoMetadataBloodTypeGeneralTypes.OptionalListOfSimpleBloodType = Field(None, description="Blood types")

    class ExpandedBloodType(BaseModel):
        blood_type_details:MaleoMetadataBloodTypeGeneralTypes.ExpandedBloodType = Field(..., description="Blood type's details")

    class OptionalExpandedBloodType(BaseModel):
        blood_type_details:MaleoMetadataBloodTypeGeneralTypes.OptionalExpandedBloodType = Field(None, description="Blood type's details")

    class ListOfExpandedBloodType(BaseModel):
        blood_types_details:MaleoMetadataBloodTypeGeneralTypes.ListOfExpandedBloodType = Field([], description="Blood types's details")

    class OptionalListOfExpandedBloodType(BaseModel):
        blood_types_details:MaleoMetadataBloodTypeGeneralTypes.OptionalListOfExpandedBloodType = Field(None, description="Blood types's details")