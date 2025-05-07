from __future__ import annotations
import os
from typing import Optional
from maleo_foundation.enums import BaseEnums
from maleo_foundation.managers.client.maleo import MaleoClientManager
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import GoogleCloudLogging
from maleo_metadata.clients.controllers.http.blood_type import MaleoMetadataBloodTypeHTTPController
from maleo_metadata.clients.controllers.http.gender import MaleoMetadataGenderHTTPController
from maleo_metadata.clients.controllers.http.organization_role import MaleoMetadataOrganizationRoleHTTPController
from maleo_metadata.clients.controllers.http.organization_type import MaleoMetadataOrganizationTypeHTTPController
from maleo_metadata.clients.controllers.http.service import MaleoMetadataServiceHTTPController
from maleo_metadata.clients.controllers.http.system_role import MaleoMetadataSystemRoleHTTPController
from maleo_metadata.clients.controllers.http.user_type import MaleoMetadataUserTypeHTTPController
from maleo_metadata.clients.controllers import (
    MaleoMetadataBloodTypeControllers,
    MaleoMetadataGenderControllers,
    MaleoMetadataOrganizationRoleControllers,
    MaleoMetadataOrganizationTypeControllers,
    MaleoMetadataServiceControllers,
    MaleoMetadataSystemRoleControllers,
    MaleoMetadataUserTypeControllers,
    MaleoMetadataControllers
)
from maleo_metadata.clients.services import (
    MaleoMetadataBloodTypeClientService,
    MaleoMetadataGenderClientService,
    MaleoMetadataOrganizationRoleClientService,
    MaleoMetadataOrganizationTypeClientService,
    MaleoMetadataServiceClientService,
    MaleoMetadataSystemRoleClientService,
    MaleoMetadataUserTypeClientService,
    MaleoMetadataServices
)

class MaleoMetadataClientManager(MaleoClientManager):
    def __init__(
        self,
        logs_dir:str,
        key:BaseTypes.OptionalString = None,
        name:BaseTypes.OptionalString = None,
        service_key:BaseTypes.OptionalString=None,
        level:BaseEnums.LoggerLevel=BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging]=None,
        url:BaseTypes.OptionalString = None
    ):
        key = "maleo-metadata" if key is None else key
        name = "MaleoMetadata" if name is None else name
        url = url or os.getenv("MALEO_METADATA_URL")
        if url is None:
            raise ValueError("MALEO_METADATA_URL environment variable must be set if url is not provided")
        super().__init__(key, name, logs_dir, service_key, level, google_cloud_logging, url)
        self._initialize_controllers()
        self._initialize_services()
        self._logger.info("Client manager initialized successfully")

    def _initialize_controllers(self):
        super()._initialize_controllers()
        #* Blood type controllers
        blood_type_http_controller = MaleoMetadataBloodTypeHTTPController(manager=self._controller_managers.http)
        blood_type_controllers = MaleoMetadataBloodTypeControllers(http=blood_type_http_controller)
        #* Gender controllers
        gender_http_controller = MaleoMetadataGenderHTTPController(manager=self._controller_managers.http)
        gender_controllers = MaleoMetadataGenderControllers(http=gender_http_controller)
        #* Organization role controllers
        organization_role_http_controller = MaleoMetadataOrganizationRoleHTTPController(manager=self._controller_managers.http)
        organization_role_controllers = MaleoMetadataOrganizationRoleControllers(http=organization_role_http_controller)
        #* Organization type controllers
        organization_type_http_controller = MaleoMetadataOrganizationTypeHTTPController(manager=self._controller_managers.http)
        organization_type_controllers = MaleoMetadataOrganizationTypeControllers(http=organization_type_http_controller)
        #* Service controllers
        service_http_controller = MaleoMetadataServiceHTTPController(manager=self._controller_managers.http)
        service_controllers = MaleoMetadataServiceControllers(http=service_http_controller)
        #* System role controllers
        system_role_http_controller = MaleoMetadataSystemRoleHTTPController(manager=self._controller_managers.http)
        system_role_controllers = MaleoMetadataSystemRoleControllers(http=system_role_http_controller)
        #* User type controllers
        user_type_http_controller = MaleoMetadataUserTypeHTTPController(manager=self._controller_managers.http)
        user_type_controllers = MaleoMetadataUserTypeControllers(http=user_type_http_controller)
        #* All controllers
        self._controllers = MaleoMetadataControllers(
            blood_type=blood_type_controllers,
            gender=gender_controllers,
            organization_role=organization_role_controllers,
            organization_type=organization_type_controllers,
            service=service_controllers,
            system_role=system_role_controllers,
            user_type=user_type_controllers
        )

    def _initialize_services(self):
        super()._initialize_services()
        blood_type_service = MaleoMetadataBloodTypeClientService(logger=self._logger, controllers=self._controllers.blood_type)
        gender_service = MaleoMetadataGenderClientService(logger=self._logger, controllers=self._controllers.gender)
        organization_role_service = MaleoMetadataOrganizationRoleClientService(logger=self._logger, controllers=self._controllers.organization_role)
        organization_type_service = MaleoMetadataOrganizationTypeClientService(logger=self._logger, controllers=self._controllers.organization_type)
        service_service = MaleoMetadataServiceClientService(logger=self._logger, controllers=self._controllers.service)
        system_role_service = MaleoMetadataSystemRoleClientService(logger=self._logger, controllers=self._controllers.system_role)
        user_type_service = MaleoMetadataUserTypeClientService(logger=self._logger, controllers=self._controllers.user_type)
        self._services = MaleoMetadataServices(
            blood_type=blood_type_service,
            gender=gender_service,
            organization_role=organization_role_service,
            organization_type=organization_type_service,
            service=service_service,
            system_role=system_role_service,
            user_type=user_type_service
        )