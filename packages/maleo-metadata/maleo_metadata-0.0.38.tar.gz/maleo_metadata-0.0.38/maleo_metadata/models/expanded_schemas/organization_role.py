from pydantic import BaseModel, Field
from maleo_metadata.types.general.organization_role import MaleoMetadataOrganizationRoleGeneralTypes

class MaleoMetadataOrganizationRoleExpandedSchemas:
    class SimpleOrganizationRole(BaseModel):
        organization_role:MaleoMetadataOrganizationRoleGeneralTypes.SimpleOrganizationRole = Field(..., description="Organization role")

    class OptionalSimpleOrganizationRole(BaseModel):
        organization_role:MaleoMetadataOrganizationRoleGeneralTypes.OptionalSimpleOrganizationRole = Field(None, description="Organization role")

    class ListOfSimpleOrganizationRole(BaseModel):
        organization_roles:MaleoMetadataOrganizationRoleGeneralTypes.ListOfSimpleOrganizationRole = Field([], description="Organization roles")

    class OptionalListOfSimpleOrganizationRole(BaseModel):
        organization_roles:MaleoMetadataOrganizationRoleGeneralTypes.OptionalListOfSimpleOrganizationRole = Field(None, description="Organization roles")

    class ExpandedOrganizationRole(BaseModel):
        organization_role_details:MaleoMetadataOrganizationRoleGeneralTypes.ExpandedOrganizationRole = Field(..., description="Organization role's details")

    class OptionalExpandedOrganizationRole(BaseModel):
        organization_role_details:MaleoMetadataOrganizationRoleGeneralTypes.OptionalExpandedOrganizationRole = Field(None, description="Organization role's details")

    class ListOfExpandedOrganizationRole(BaseModel):
        organization_roles_details:MaleoMetadataOrganizationRoleGeneralTypes.ListOfExpandedOrganizationRole = Field([], description="Organization roles's details")

    class OptionalListOfExpandedOrganizationRole(BaseModel):
        organization_roles_details:MaleoMetadataOrganizationRoleGeneralTypes.OptionalExpandedOrganizationRole = Field(None, description="Organization roles's details")