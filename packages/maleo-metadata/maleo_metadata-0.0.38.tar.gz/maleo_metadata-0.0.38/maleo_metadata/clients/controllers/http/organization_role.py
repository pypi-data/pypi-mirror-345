from maleo_foundation.managers.client.maleo import ClientHTTPController
from maleo_foundation.models.transfers.results.client.controllers.http import BaseClientHTTPControllerResults
from maleo_metadata.models.transfers.parameters.general.organization_role import MaleoMetadataOrganizationRoleGeneralParametersTransfers
from maleo_metadata.models.transfers.parameters.client.organization_role import MaleoMetadataOrganizationRoleClientParametersTransfers

class MaleoMetadataOrganizationRoleHTTPController(ClientHTTPController):
    async def get_organization_roles(self, parameters:MaleoMetadataOrganizationRoleClientParametersTransfers.GetMultiple) -> BaseClientHTTPControllerResults:
        """Fetch organization roles from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/organization-roles/"

            #* Parse parameters to query params
            params = MaleoMetadataOrganizationRoleClientParametersTransfers.GetMultipleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)

    async def get_organization_role(self, parameters:MaleoMetadataOrganizationRoleGeneralParametersTransfers.GetSingle) -> BaseClientHTTPControllerResults:
        """Fetch organization role from MaleoMetadata"""
        async with self._manager.client as client:
            #* Define URL
            url = f"{self._manager.url.api}/v1/organization-roles/{parameters.identifier}/{parameters.value}"

            #* Parse parameters to query params
            params = MaleoMetadataOrganizationRoleGeneralParametersTransfers.GetSingleQuery.model_validate(parameters.model_dump()).model_dump(exclude_none=True)

            #* Send request and wait for response
            response = await client.get(url=url, params=params)
            return BaseClientHTTPControllerResults(response=response)