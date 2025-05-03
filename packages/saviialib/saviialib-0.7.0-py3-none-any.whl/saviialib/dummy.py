from services.epii.api import EpiiAPI
from general_types.api.update_thies_data_types import EpiiUpdateThiesConfig
import asyncio


async def main():
    api = EpiiAPI()
    config = EpiiUpdateThiesConfig(
        ftp_host="192.168.1.153",
        ftp_password="12345678",
        ftp_user="anonymous",
        ftp_port=2121,
        sharepoint_client_id="5cc9b69f-0e49-419c-97be-0c5b4048bf94",
        sharepoint_client_secret="Snf8Q~vSYLkEHWc6MCgHAmPEMI9j8egA6fTz7aFh",
        sharepoint_site_name="uc365_CentrosyEstacionesRegionalesUC",
        sharepoint_tenant_id="5ff5d9fa-f83f-4ac1-a4d2-eb48ea0a00d2",
        sharepoint_tenant_name="uccl0",
    )
    response = await api.update_thies_data(config)
    print(response)


asyncio.run(main())
