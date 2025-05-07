from __future__ import annotations
from .blood_type import MaleoMetadataBloodTypeExpandedSchemas
from .gender import MaleoMetadataGenderExpandedSchemas
from .organization_role import MaleoMetadataOrganizationRoleExpandedSchemas
from .organization_type import MaleoMetadataOrganizationTypeExpandedSchemas
from .service import MaleoMetadataServiceExpandedSchemas
from .system_role import MaleoMetadataSystemRoleExpandedSchemas
from .user_type import MaleoMetadataUserTypeExpandedSchemas

class MaleoMetadataExpandedSchemas:
    BloodType = MaleoMetadataBloodTypeExpandedSchemas
    Genders = MaleoMetadataGenderExpandedSchemas
    OrganizationRoles = MaleoMetadataOrganizationRoleExpandedSchemas
    OrganizationTypes = MaleoMetadataOrganizationTypeExpandedSchemas
    Services = MaleoMetadataServiceExpandedSchemas
    SystemRoles = MaleoMetadataSystemRoleExpandedSchemas
    UserType = MaleoMetadataUserTypeExpandedSchemas