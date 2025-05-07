from fastapi import status
from maleo_foundation.managers.client.maleo import ClientService
from maleo_foundation.utils.exceptions import BaseExceptions
from maleo_metadata.clients.controllers import MaleoMetadataUserTypeControllers
from maleo_metadata.enums.general import MaleoMetadataGeneralEnums
from maleo_metadata.models.transfers.parameters.general.user_type import MaleoMetadataUserTypeGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.user_type import MaleoMetadataUserTypeClientParametersTransfers
from maleo_metadata.models.transfers.results.general.user_type import MaleoMetadataUserTypeGeneralResultsTransfers
from maleo_metadata.types.results.general.user_type import MaleoMetadataUserTypeGeneralResultsTypes

class MaleoMetadataUserTypeClientService(ClientService):
    def __init__(self, logger, controllers:MaleoMetadataUserTypeControllers):
        super().__init__(logger)
        self._controllers = controllers

    @property
    def controllers(self) -> MaleoMetadataUserTypeControllers:
        raise self._controllers

    async def get_user_types(
        self,
        parameters:MaleoMetadataUserTypeClientParametersTransfers.GetMultiple,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataUserTypeGeneralResultsTypes.GetMultiple:
        """Retrieve user types from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving user types",
            logger=self._logger,
            fail_result_class=MaleoMetadataUserTypeGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataUserTypeGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve user types using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_user_types(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataUserTypeGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                return MaleoMetadataUserTypeGeneralResultsTransfers.Fail.model_validate(controller_result.content)
            else:
                if controller_result.content["data"] is None:
                    return MaleoMetadataUserTypeGeneralResultsTransfers.NoData.model_validate(controller_result.content)
                else:
                    return MaleoMetadataUserTypeGeneralResultsTransfers.MultipleData.model_validate(controller_result.content)
        return await _impl()

    async def get_user_type(
        self,
        parameters:MaleoMetadataUserTypeGeneralParametersTransfers.GetSingle,
        controller_type:MaleoMetadataGeneralEnums.ClientControllerType = MaleoMetadataGeneralEnums.ClientControllerType.HTTP
    ) -> MaleoMetadataUserTypeGeneralResultsTypes.GetSingle:
        """Retrieve user type from MaleoMetadata"""
        @BaseExceptions.service_exception_handler(
            operation="retrieving user type",
            logger=self._logger,
            fail_result_class=MaleoMetadataUserTypeGeneralResultsTransfers.Fail
        )
        async def _impl():
            #* Validate chosen controller type
            if not isinstance(controller_type, MaleoMetadataGeneralEnums.ClientControllerType):
                message = "Invalid controller type"
                description = "The provided controller type did not exists"
                return MaleoMetadataUserTypeGeneralResultsTransfers.Fail(message=message, description=description)
            #* Retrieve user type using chosen controller
            if controller_type == MaleoMetadataGeneralEnums.ClientControllerType.HTTP:
                controller_result = await self._controllers.http.get_user_type(parameters=parameters)
            else:
                message = "Invalid controller type"
                description = "The provided controller type has not been implemented"
                return MaleoMetadataUserTypeGeneralResultsTransfers.Fail(message=message, description=description)
            #* Return proper response
            if not controller_result.success:
                if controller_result.status_code != status.HTTP_404_NOT_FOUND:
                    return MaleoMetadataUserTypeGeneralResultsTransfers.Fail.model_validate(controller_result.content)
                else:
                    return MaleoMetadataUserTypeGeneralResultsTransfers.NoData.model_validate(controller_result.content)
            else:
                return MaleoMetadataUserTypeGeneralResultsTransfers.SingleData.model_validate(controller_result.content)
        return await _impl()