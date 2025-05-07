from pydantic import BaseModel, Field
from maleo_metadata.types.general.system_role import MaleoMetadataSystemRoleGeneralTypes

class MaleoMetadataSystemRoleExpandedSchemas:
    class SimpleSystemRole(BaseModel):
        system_role:MaleoMetadataSystemRoleGeneralTypes.SimpleSystemRole = Field(..., description="System role")

    class OptionalSimpleSystemRole(BaseModel):
        system_role:MaleoMetadataSystemRoleGeneralTypes.OptionalSimpleSystemRole = Field(None, description="System role")

    class ListOfSimpleSystemRole(BaseModel):
        system_roles:MaleoMetadataSystemRoleGeneralTypes.ListOfSimpleSystemRole = Field([], description="System roles")

    class OptionalListOfSimpleSystemRole(BaseModel):
        system_roles:MaleoMetadataSystemRoleGeneralTypes.OptionalListOfSimpleSystemRole = Field(None, description="System roles")

    class ExpandedSystemRole(BaseModel):
        system_role_details:MaleoMetadataSystemRoleGeneralTypes.ExpandedSystemRole = Field(..., description="System role's details")

    class OptionalExpandedSystemRole(BaseModel):
        system_role_details:MaleoMetadataSystemRoleGeneralTypes.OptionalExpandedSystemRole = Field(None, description="System role's details")

    class ListOfExpandedSystemRole(BaseModel):
        system_roles_details:MaleoMetadataSystemRoleGeneralTypes.ListOfExpandedSystemRole = Field([], description="System roles's details")

    class OptionalListOfExpandedSystemRole(BaseModel):
        system_roles_details:MaleoMetadataSystemRoleGeneralTypes.OptionalListOfExpandedSystemRole = Field(None, description="System role's details")