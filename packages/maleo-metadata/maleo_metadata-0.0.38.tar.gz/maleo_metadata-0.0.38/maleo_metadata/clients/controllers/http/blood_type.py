from maleo_foundation.managers.client.maleo import ClientHTTPController
from maleo_foundation.models.transfers.results.client.controllers.http import BaseClientHTTPControllerResults
from maleo_metadata.models.transfers.parameters.general.blood_type import MaleoMetadataBloodTypeGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.blood_type import MaleoMetadataBloodTypeClientParametersTransfers

class MaleoMetadataBloodTypeHTTPController(ClientHTTPController):
    async def get_blood_types(self, parameters:MaleoMetadataBloodTypeClientParametersTransfers.GetMultiple) -> BaseClientHTTPControllerResults:
        """Fetch blood types from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/blood-types/"

            #* Parse parameters to query params
            params = MaleoMetadataBloodTypeClientParametersTransfers.GetMultipleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)

    async def get_blood_type(self, parameters:MaleoMetadataBloodTypeGeneralParametersTransfers.GetSingle) -> BaseClientHTTPControllerResults:
        """Fetch blood type from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/blood-types/{parameters.identifier}/{parameters.value}"

            #* Parse parameters to query params
            params = MaleoMetadataBloodTypeGeneralParametersTransfers.GetSingleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)