from pydantic import BaseModel, Field
from maleo_metadata.types.general.service import MaleoMetadataServiceGeneralTypes

class MaleoMetadataServiceExpandedSchemas:
    class SimpleService(BaseModel):
        service:MaleoMetadataServiceGeneralTypes.SimpleService = Field(..., description="Service")

    class OptionalService(BaseModel):
        service:MaleoMetadataServiceGeneralTypes.OptionalSimpleService = Field(None, description="Service")

    class ListOfSimpleService(BaseModel):
        services:MaleoMetadataServiceGeneralTypes.ListOfSimpleService = Field([], description="Services")

    class OptionalListOfSimpleService(BaseModel):
        services:MaleoMetadataServiceGeneralTypes.OptionalListOfSimpleService = Field(None, description="Services")

    class ExpandedService(BaseModel):
        service_details:MaleoMetadataServiceGeneralTypes.ExpandedService = Field(..., description="Service's details")

    class OptionalExpandedService(BaseModel):
        service_details:MaleoMetadataServiceGeneralTypes.OptionalExpandedService = Field(None, description="Service's details")

    class ListOfExpandedService(BaseModel):
        services_details:MaleoMetadataServiceGeneralTypes.ListOfExpandedService = Field([], description="Services's details")

    class OptionalListOfExpandedService(BaseModel):
        services_details:MaleoMetadataServiceGeneralTypes.OptionalListOfExpandedService = Field(None, description="Services's details")