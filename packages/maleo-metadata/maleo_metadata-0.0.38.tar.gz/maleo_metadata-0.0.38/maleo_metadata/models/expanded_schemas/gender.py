from pydantic import BaseModel, Field
from maleo_metadata.types.general.gender import MaleoMetadataGenderGeneralTypes

class MaleoMetadataGenderExpandedSchemas:
    class SimpleGender(BaseModel):
        gender:MaleoMetadataGenderGeneralTypes.SimpleGender = Field(..., description="Gender")

    class OptionalSimpleGender(BaseModel):
        gender:MaleoMetadataGenderGeneralTypes.OptionalSimpleGender = Field(None, description="Gender")

    class ListOfSimpleGender(BaseModel):
        genders:MaleoMetadataGenderGeneralTypes.ListOfSimpleGender = Field([], description="Genders")

    class OptionalListOfSimpleGender(BaseModel):
        genders:MaleoMetadataGenderGeneralTypes.OptionalListOfSimpleGender = Field(None, description="Genders")

    class ExpandedGender(BaseModel):
        gender_details:MaleoMetadataGenderGeneralTypes.ExpandedGender = Field(..., description="Gender's details")

    class OptionalExpandedGender(BaseModel):
        gender_details:MaleoMetadataGenderGeneralTypes.OptionalExpandedGender = Field(None, description="Gender's details")

    class ListOfExpandedGender(BaseModel):
        genders_details:MaleoMetadataGenderGeneralTypes.ListOfExpandedGender = Field([], description="Genders's details")

    class OptionalListOfExpandedGender(BaseModel):
        genders_details:MaleoMetadataGenderGeneralTypes.OptionalListOfExpandedGender = Field(None, description="Genders's details")