from pydantic import BaseModel, Field
from maleo_metadata.types.general.organization_type import MaleoMetadataOrganizationTypeGeneralTypes

class MaleoMetadataOrganizationTypeExpandedSchemas:
    class SimpleOrganizationType(BaseModel):
        organization_type:MaleoMetadataOrganizationTypeGeneralTypes.SimpleOrganizationType = Field(..., description="Organization type")

    class OptionalSimpleOrganizationType(BaseModel):
        organization_type:MaleoMetadataOrganizationTypeGeneralTypes.OptionalSimpleOrganizationType = Field(None, description="Organization type")

    class ListOfSimpleOrganizationType(BaseModel):
        organization_types:MaleoMetadataOrganizationTypeGeneralTypes.ListOfSimpleOrganizationType = Field([], description="Organization types")

    class OptionalListOfSimpleOrganizationType(BaseModel):
        organization_types:MaleoMetadataOrganizationTypeGeneralTypes.OptionalListOfSimpleOrganizationType = Field(None, description="Organization types")

    class ExpandedOrganizationType(BaseModel):
        organization_type_details:MaleoMetadataOrganizationTypeGeneralTypes.ExpandedOrganizationType = Field(..., description="Organization type's details")

    class OptionalExpandedOrganizationType(BaseModel):
        organization_type_details:MaleoMetadataOrganizationTypeGeneralTypes.OptionalExpandedOrganizationType = Field(None, description="Organization type's details")

    class ListOfExpandedOrganizationType(BaseModel):
        organization_types_details:MaleoMetadataOrganizationTypeGeneralTypes.ListOfExpandedOrganizationType = Field([], description="Organization types's details")

    class OptionalListOfExpandedOrganizationType(BaseModel):
        organization_types_details:MaleoMetadataOrganizationTypeGeneralTypes.OptionalListOfSimpleOrganizationType = Field(None, description="Organization types's details")