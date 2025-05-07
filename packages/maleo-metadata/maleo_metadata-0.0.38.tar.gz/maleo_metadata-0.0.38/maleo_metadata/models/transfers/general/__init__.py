from __future__ import annotations
from .blood_type import BloodTypeTransfers
from .gender import GenderTransfers
from .organization_role import OrganizationRoleTransfers
from .organization_type import OrganizationTypeTransfers
from .service import ServiceTransfers
from .system_role import SystemRoleTransfers
from .user_type import UserTypeTransfers

class MaleoMetadataGeneralTransfers:
    BloodType = BloodTypeTransfers
    Gender = GenderTransfers
    OrganizationRole = OrganizationRoleTransfers
    OrganizationType = OrganizationTypeTransfers
    Service = ServiceTransfers
    SystemRole = SystemRoleTransfers
    UserType = UserTypeTransfers