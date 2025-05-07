from fastapi import status
from maleo_foundation.managers.client.maleo import ClientService
from maleo_foundation.utils.exceptions import BaseExceptions
from maleo_metadata.clients.controllers import MaleoMetadataOrganizationRoleControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.organization_role import MaleoMetadataOrganizationRoleGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.organization_role import MaleoMetadataOrganizationRoleClientParametersTransfers
from maleo_metadata.models.transfers.results.general.organization_role import MaleoMetadataOrganizationRoleGeneralResultsTransfers
from maleo_metadata.types.results.general.organization_role import MaleoMetadataOrganizationRoleGeneralResultsTypes

class MaleoMetadataOrganizationRoleClientService(ClientService):
    def __init__(self, logger, controllers:MaleoMetadataOrganizationRoleControllers):
        super().__init__(logger)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataOrganizationRoleControllers:
        raise self._controllers

    async def get_organization_roles(
        self,
        parameters:MaleoMetadataOrganizationRoleClientParametersTransfers.GetMultiple,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataOrganizationRoleGeneralResultsTypes.GetMultiple:
        """Retrieve organization roles from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving organization roles",
            logger=self._logger,
            fail_result_class=MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve organization roles using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_organization_roles(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail.model_validate(controller_result.content)
            else:
                if controller_result.content["data"] is None:
                    return MaleoMetadataOrganizationRoleGeneralResultsTransfers.NoData.model_validate(controller_result.content)
                else:
                    return MaleoMetadataOrganizationRoleGeneralResultsTransfers.MultipleData.model_validate(controller_result.content)
        return await _impl()

    async def get_organization_role(
        self,
        parameters:MaleoMetadataOrganizationRoleGeneralParametersTransfers.GetSingle,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataOrganizationRoleGeneralResultsTypes.GetSingle:
        """Retrieve organization role from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving organization role",
            logger=self._logger,
            fail_result_class=MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve organization role using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_organization_role(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                if controller_result.status_code != status.HTTP_404_NOT_FOUND:
                    return MaleoMetadataOrganizationRoleGeneralResultsTransfers.Fail.model_validate(controller_result.content)
                else:
                    return MaleoMetadataOrganizationRoleGeneralResultsTransfers.NoData.model_validate(controller_result.content)
            else:
                return MaleoMetadataOrganizationRoleGeneralResultsTransfers.SingleData.model_validate(controller_result.content)
        return await _impl()