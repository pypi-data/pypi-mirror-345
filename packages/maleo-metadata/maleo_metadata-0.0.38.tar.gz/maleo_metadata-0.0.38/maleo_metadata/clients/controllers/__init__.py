from __future__ import annotations
from pydantic import Field
from maleo_foundation.managers.client.maleo import ClientServiceControllers, ClientControllers

from maleo_metadata.clients.controllers.http.blood_type import MaleoMetadataBloodTypeHTTPController
class MaleoMetadataBloodTypeControllers(ClientServiceControllers):
    http:MaleoMetadataBloodTypeHTTPController = Field(..., description="Blood type's http controller")

from maleo_metadata.clients.controllers.http.gender import MaleoMetadataGenderHTTPController
class MaleoMetadataGenderControllers(ClientServiceControllers):
    http:MaleoMetadataGenderHTTPController = Field(..., description="Gender's http controller")

from maleo_metadata.clients.controllers.http.organization_role import MaleoMetadataOrganizationRoleHTTPController
class MaleoMetadataOrganizationRoleControllers(ClientServiceControllers):
    http:MaleoMetadataOrganizationRoleHTTPController = Field(..., description="Organization role's http controller")

from maleo_metadata.clients.controllers.http.organization_type import MaleoMetadataOrganizationTypeHTTPController
class MaleoMetadataOrganizationTypeControllers(ClientServiceControllers):
    http:MaleoMetadataOrganizationTypeHTTPController = Field(..., description="Organization type's http controller")

from maleo_metadata.clients.controllers.http.service import MaleoMetadataServiceHTTPController
class MaleoMetadataServiceControllers(ClientServiceControllers):
    http:MaleoMetadataServiceHTTPController = Field(..., description="Service's http controller")

from maleo_metadata.clients.controllers.http.system_role import MaleoMetadataSystemRoleHTTPController
class MaleoMetadataSystemRoleControllers(ClientServiceControllers):
    http:MaleoMetadataSystemRoleHTTPController = Field(..., description="System role's http controller")

from maleo_metadata.clients.controllers.http.user_type import MaleoMetadataUserTypeHTTPController
class MaleoMetadataUserTypeControllers(ClientServiceControllers):
    http:MaleoMetadataUserTypeHTTPController = Field(..., description="User type's http controller")

class MaleoMetadataControllers(ClientControllers):
    blood_type:MaleoMetadataBloodTypeControllers = Field(..., description="Blood type's controllers")
    gender:MaleoMetadataGenderControllers = Field(..., description="Gender's controllers")
    organization_role:MaleoMetadataOrganizationRoleControllers = Field(..., description="Organization role's controllers")
    organization_type:MaleoMetadataOrganizationTypeControllers = Field(..., description="Organization type's controllers")
    service:MaleoMetadataServiceControllers = Field(..., description="Service's controllers")
    system_role:MaleoMetadataSystemRoleControllers = Field(..., description="System role's controllers")
    user_type:MaleoMetadataUserTypeControllers = Field(..., description="User type's controllers")