from fastapi import status
from maleo_foundation.managers.client.maleo import ClientService
from maleo_foundation.utils.exceptions import BaseExceptions
from maleo_metadata.clients.controllers import MaleoMetadataSystemRoleControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.system_role import MaleoMetadataSystemRoleGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.system_role import MaleoMetadataSystemRoleClientParametersTransfers
from maleo_metadata.models.transfers.results.general.system_role import MaleoMetadataSystemRoleGeneralResultsTransfers
from maleo_metadata.types.results.general.system_role import MaleoMetadataSystemRoleGeneralResultsTypes

class MaleoMetadataSystemRoleClientService(ClientService):
    def __init__(self, logger, controllers:MaleoMetadataSystemRoleControllers):
        super().__init__(logger)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataSystemRoleControllers:
        raise self._controllers

    async def get_system_roles(
        self,
        parameters:MaleoMetadataSystemRoleClientParametersTransfers.GetMultiple,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataSystemRoleGeneralResultsTypes.GetMultiple:
        """Retrieve system roles from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving system roles",
            logger=self._logger,
            fail_result_class=MaleoMetadataSystemRoleGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve system roles using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_system_roles(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail.model_validate(controller_result.content)
            else:
                if controller_result.content["data"] is None:
                    return MaleoMetadataSystemRoleGeneralResultsTransfers.NoData.model_validate(controller_result.content)
                else:
                    return MaleoMetadataSystemRoleGeneralResultsTransfers.MultipleData.model_validate(controller_result.content)
        return await _impl()

    async def get_system_role(
        self,
        parameters:MaleoMetadataSystemRoleGeneralParametersTransfers.GetSingle,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataSystemRoleGeneralResultsTypes.GetSingle:
        """Retrieve system role from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving system role",
            logger=self._logger,
            fail_result_class=MaleoMetadataSystemRoleGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve system role using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_system_role(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                if controller_result.status_code != status.HTTP_404_NOT_FOUND:
                    return MaleoMetadataSystemRoleGeneralResultsTransfers.Fail.model_validate(controller_result.content)
                else:
                    return MaleoMetadataSystemRoleGeneralResultsTransfers.NoData.model_validate(controller_result.content)
            else:
                return MaleoMetadataSystemRoleGeneralResultsTransfers.SingleData.model_validate(controller_result.content)
        return await _impl()