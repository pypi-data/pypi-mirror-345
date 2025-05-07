from maleo_foundation.managers.client.maleo import ClientHTTPController
from maleo_foundation.models.transfers.results.client.controllers.http import BaseClientHTTPControllerResults
from maleo_metadata.models.transfers.parameters.general.service import MaleoMetadataServiceGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.service import MaleoMetadataServiceClientParametersTransfers

class MaleoMetadataServiceHTTPController(ClientHTTPController):
    async def get_services(self, parameters:MaleoMetadataServiceClientParametersTransfers.GetMultiple) -> BaseClientHTTPControllerResults:
        """Fetch services from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/services/"

            #* Parse parameters to query params
            params = MaleoMetadataServiceClientParametersTransfers.GetMultipleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)

    async def get_service(self, parameters:MaleoMetadataServiceGeneralParametersTransfers.GetSingle) -> BaseClientHTTPControllerResults:
        """Fetch service from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/services/{parameters.identifier}/{parameters.value}"

            #* Parse parameters to query params
            params = MaleoMetadataServiceGeneralParametersTransfers.GetSingleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)