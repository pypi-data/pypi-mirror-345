from .module_imports import get_key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    delete,
    get as http_get,
    patch,
    post,
    returns,
    headers,
    retry,
    Body,
    json,
    Query,
)

USE_SERVICES_API = True

key = get_key(use_services_api=USE_SERVICES_API)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Technical_Content_Feedback(Consumer):
    """Interface to Technical Content Feedback resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=self._base_url, *args, **kw)

    def entries(self):
        return self.__Entries(self)

    def productGroups(self):
        return self.__Product_Groups(self)

    def productLines(self):
        return self.__Product_Lines(self)

    def contentTypes(self):
        return self.__Content_Types(self)

    def administrators(self):
        return self.__Administrators(self)

    def assignments(self):
        return self.__Assignments(self)

    def logs(self):
        return self.__Logs(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Entries(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/entries")
        def list(
            self,
            status: Query = None,
            priority: Query = None,
            product_group_uid: Query = None,
            brand_uid: Query = None,
            product_line_uid: Query = None,
            content_type_uid: Query = None,
            administrator_uid: Query = None,
            company_uid: Query = None,
            machine_uid: Query = None,
        ):
            """This call will return detailed technical content feedback information for the specified criteria."""

        @returns.json
        @http_get("technical-content-feedback/entries/{uid}")
        def get(
            self,
            uid: str,
        ):
            """This call will return detailed technical content feedback information for the specified criteria."""

        @delete("technical-content-feedback/entries/{uid}")
        def delete(self, uid: str):
            """This call will delete the technical content feedback for the specified uid."""

        @returns.json
        @json
        @post("technical-content-feedback/entries")
        def insert(self, entry: Body):
            """This call will create a technical content feedback with the specified parameters."""

        @json
        @patch("technical-content-feedback/entries/{uid}")
        def update(self, uid: str, entry: Body):
            """This call will update the technical content feedback with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Logs(Consumer):
        """Interface to Technical Content Feedback Logs resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/logs")
        def list(self):
            """This call will return a list of log information."""

        @returns.json
        @http_get("technical-content-feedback/logs/{log_uid}")
        def get(self, log_uid: str):
            """This call will return log information for the specified log uid."""

        @delete("technical-content-feedback/logs/{log_uid}")
        def delete(self, log_uid: str):
            """This call will delete the log information for the specified log uid."""

        @json
        @patch("technical-content-feedback/logs/{log_uid}")
        def update(self, log_uid: str, log: Body):
            """This call will update the log information with the specified parameters."""

        @returns.json
        @http_get("technical-content-feedback/entries/{entry_uid}/logs")
        def list_by_entry(
            self,
            entry_uid: str,
        ):
            """This call will return log information for the specified entry uid."""

        @returns.json
        @json
        @post("technical-content-feedback/entries/{entry_uid}/logs")
        def insert(self, entry_uid: str, log: Body):
            """This call will create log information with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Product_Groups(Consumer):
        """Interface to Technical Content Feedback Product Groups resource for the RockyRoad API."""
        
        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)
        
        @returns.json
        @http_get("technical-content-feedback/product-groups")
        def list(self):
            """This call will return a list of product groups."""
        
        @returns.json
        @http_get("technical-content-feedback/product-groups/{uid}")
        def get(self, uid: str):
            """This call will return a product group for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/product-groups")
        def insert(self, product_group: Body):
            """This call will create a product group with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/product-groups/{uid}")
        def update(self, uid: str, product_group: Body):
            """This call will update the product group with the specified parameters."""
        
        @delete("technical-content-feedback/product-groups/{uid}")
        def delete(self, uid: str):
            """This call will delete the product group for the specified uid."""



    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Product_Lines(Consumer):
        """Interface to Technical Content Feedback Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/product-lines")
        def list(self):
            """This call will return a list of product lines."""
        
        @returns.json
        @http_get("technical-content-feedback/product-lines/{uid}")
        def get(self, uid: str):
            """This call will return a product line for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/product-lines")
        def insert(self, product_line: Body):
            """This call will create a product line with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/product-lines/{uid}")
        def update(self, uid: str, product_line: Body):
            """This call will update the product line with the specified parameters."""
        
        @delete("technical-content-feedback/product-lines/{uid}")
        def delete(self, uid: str):
            """This call will delete the product line for the specified uid."""

    

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Content_Types(Consumer):
        """Interface to Technical Content Feedback Content Types resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/content-types")
        def list(self):
            """This call will return a list of content types."""
        
        @returns.json
        @http_get("technical-content-feedback/content-types/{uid}")
        def get(self, uid: str):
            """This call will return a content type for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/content-types")
        def insert(self, content_type: Body):
            """This call will create a content type with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/content-types/{uid}")
        def update(self, uid: str, content_type: Body):
            """This call will update the content type with the specified parameters."""
        
        @delete("technical-content-feedback/content-types/{uid}")
        def delete(self, uid: str):
            """This call will delete the content type for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Administrators(Consumer):
        """Interface to Technical Content Feedback Administrators resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/administrators")
        def list(self):
            """This call will return a list of administrators."""
        
        @returns.json
        @http_get("technical-content-feedback/administrators/{uid}")
        def get(self, uid: str):
            """This call will return an administrator for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/administrators")
        def insert(self, administrator: Body):
            """This call will create an  administrator with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/administrators/{uid}")
        def update(self, uid: str, administrator: Body):
            """This call will update the administrator with the specified parameters."""
        
        @delete("technical-content-feedback/administrators/{uid}")
        def delete(self, uid: str):
            """This call will delete the administrator for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Assignments(Consumer):
        """Interface to Technical Content Feedback Assignments resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/assignments")
        def list(self):
            """This call will return a list of assignments."""
        
        @returns.json
        @http_get("technical-content-feedback/assignments/{uid}")
        def get(self, uid: str):
            """This call will return an assignment for the specified uid."""

        @returns.json
        @http_get("technical-content-feedback/assignments-matrix")
        def matrix(self):
            """This call will return a matrix of assignments."""
        
        @returns.json
        @json
        @post("technical-content-feedback/assignments")
        def insert(self, assignment: Body):
            """This call will create an assignment with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/assignments/{uid}")
        def update(self, uid: str, assignment: Body):
            """This call will update the assignment with the specified parameters."""
        
        @delete("technical-content-feedback/assignments/{uid}")
        def delete(self, uid: str):
            """This call will delete the assignment for the specified uid."""