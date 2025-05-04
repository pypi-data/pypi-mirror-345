from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Portal_Configurations(Consumer):
    """Inteface to portal configurations resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("portal/configurations/file-resources")
    def get_file_resources(
        self,
    ):
        """This call will return portal configurations for file resources."""

    @returns.json
    @http_get("portal/configurations/parts-lookup-data-files")
    def get_parts_lookup_data_files(
        self,
    ):
        """This call will return portal configurations for parts lookup data files."""

    @returns.json
    @http_get("portal/configurations/parts-lookup-fixed-width-settings")
    def get_parts_lookup_fixed_width_settings(
        self,
    ):
        """This call will return portal configurations for parts lookup fixed width settings."""
