from loguru import logger
from pythonik.models.base import Response
from pythonik.models.metadata.views import (
    ViewMetadata,
    CreateViewRequest,
    UpdateViewRequest,
)
from pythonik.models.metadata.view_responses import ViewResponse, ViewListResponse
from pythonik.models.mutation.metadata.mutate import (
    UpdateMetadata,
    UpdateMetadataResponse,
)
from pythonik.specs.base import Spec
from typing import Literal, Union, Dict, Any, List


# Asset metadata paths
ASSET_METADATA_FROM_VIEW_PATH = "assets/{}/views/{}"
UPDATE_ASSET_METADATA = "assets/{}/views/{}/"
ASSET_OBJECT_VIEW_PATH = "assets/{}/{}/{}/views/{}/"
PUT_METADATA_DIRECT_PATH = "{}/{}/"

# View paths
VIEWS_BASE = "views/"
CREATE_VIEW_PATH = VIEWS_BASE
GET_VIEW_PATH = VIEWS_BASE + "{view_id}/"
UPDATE_VIEW_PATH = GET_VIEW_PATH
DELETE_VIEW_PATH = GET_VIEW_PATH


ObjectType = Literal["segments"]


class MetadataSpec(Spec):
    server = "API/metadata/"

    def get_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """Given an asset id and the asset's view id, fetch metadata from the asset's view

        Args:
            asset_id: The asset ID to get metadata for
            view_id: The view ID to get metadata from
            intercept_404: Iconik returns a 404 when a view has no metadata, intercept_404 will intercept that error
                and return the ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful using this.
            Call raise_for_status_404 if you still want to raise status on 404 error
        """
        resp = self._get(
            ASSET_METADATA_FROM_VIEW_PATH.format(asset_id, view_id), **kwargs
        )

        if intercept_404 and resp.status_code == 404:
            parsed_response = self.parse_response(resp, ViewMetadata)
            parsed_response.data = intercept_404
            parsed_response.response.raise_for_status_404 = (
                parsed_response.response.raise_for_status
            )

            parsed_response.response.raise_for_status = lambda: logger.warning(
                "raise for status disabled due to intercept_404, please call"
                " raise_for_status_404 to throw an error on 404"
            )
            return parsed_response

        return self.parse_response(resp, ViewMetadata)

    def update_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Given an asset's view id, update metadata in asset's view

        Args:
            asset_id: The asset ID to update metadata for
            view_id: The view ID to update metadata in
            metadata: The metadata to update, either as UpdateMetadata model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request
        """
        json_data = self._prepare_model_data(
            metadata, exclude_defaults=exclude_defaults
        )
        resp = self._put(
            UPDATE_ASSET_METADATA.format(asset_id, view_id), json=json_data, **kwargs
        )

        return self.parse_response(resp, UpdateMetadataResponse)

    def put_metadata_direct(
        self,
        object_type: str,
        object_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Edit metadata values directly without a view.

        Args:
            object_type: The type of object to update metadata for
            object_id: The unique identifier of the object
            metadata: Metadata values to update, either as UpdateMetadata model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response[UpdateMetadataResponse]

        Required roles:
            - admin_access

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 403 Forbidden (non-admin user)
            - 404 Object not found

        Note:
            Use with caution. This method bypasses standard validation checks for speed,
            and will write to the database even if the object_id doesn't exist. Admin
            access required as this is a potentially dangerous operation.
        """
        json_data = self._prepare_model_data(
            metadata, exclude_defaults=exclude_defaults
        )
        resp = self._put(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id),
            json=json_data,
            **kwargs,
        )

        return self.parse_response(resp, UpdateMetadataResponse)

    def put_object_view_metadata(
        self,
        asset_id: str,
        object_type: ObjectType,
        object_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Put metadata for a specific sub-object view of an asset

        Args:
            asset_id: The asset ID to update metadata for
            object_type: The type of object to update metadata for
            object_id: The object ID to update metadata for
            view_id: The view ID to update metadata in
            metadata: The metadata to update, either as UpdateMetadata model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request
        """
        json_data = self._prepare_model_data(
            metadata, exclude_defaults=exclude_defaults
        )
        endpoint = ASSET_OBJECT_VIEW_PATH.format(
            asset_id, object_type, object_id, view_id
        )
        resp = self._put(endpoint, json=json_data, **kwargs)

        return self.parse_response(resp, UpdateMetadataResponse)

    def put_segment_view_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Put metadata for a segment view (backwards compatibility wrapper)

        Args:
            asset_id: The asset ID to update metadata for
            segment_id: The segment ID to update metadata for
            view_id: The view ID to update metadata in
            metadata: The metadata to update, either as UpdateMetadata model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request
        """
        return self.put_object_view_metadata(
            asset_id=asset_id,
            object_type="segments",
            object_id=segment_id,
            view_id=view_id,
            metadata=metadata,
            exclude_defaults=exclude_defaults,
            **kwargs,
        )

    def put_segment_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Put metadata for a segment of an asset

        Args:
            asset_id: The asset ID to update metadata for
            segment_id: The segment ID to update metadata for
            view_id: The view ID to update metadata in
            metadata: The metadata to update, either as UpdateMetadata model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request
        """
        return self.put_object_view_metadata(
            asset_id,
            "segments",
            segment_id,
            view_id,
            metadata,
            exclude_defaults=exclude_defaults,
            **kwargs,
        )

    def create_view(
        self,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Create a new view in Iconik.

        Args:
            view: The view to create, either as CreateViewRequest model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_write_metadata_views

        Returns:
            Response: The created view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
        """
        json_data = self._prepare_model_data(view, exclude_defaults=exclude_defaults)
        resp = self._post(CREATE_VIEW_PATH, json=json_data, **kwargs)
        return self.parse_response(resp, ViewResponse)

    def update_view(
        self,
        view_id: str,
        view: Union[UpdateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Update an existing view in Iconik.

        Args:
            view_id: ID of the view to update
            view: The view updates, either as UpdateViewRequest model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_write_metadata_views

        Returns:
            Response: The updated view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        json_data = self._prepare_model_data(view, exclude_defaults=exclude_defaults)
        resp = self._patch(
            UPDATE_VIEW_PATH.format(view_id=view_id), json=json_data, **kwargs
        )
        return self.parse_response(resp, ViewResponse)

    def replace_view(
        self,
        view_id: str,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """Replace an existing view in Iconik with a new one.

        Unlike update_view which allows partial updates, this method requires all fields
        to be specified as it completely replaces the view.

        Args:
            view_id: ID of the view to replace
            view: The complete new view data, either as CreateViewRequest model or dict
            exclude_defaults: Whether to exclude default values when dumping Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_write_metadata_views

        Returns:
            Response: The replaced view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        json_data = self._prepare_model_data(view, exclude_defaults=exclude_defaults)
        resp = self._put(
            UPDATE_VIEW_PATH.format(view_id=view_id), json=json_data, **kwargs
        )
        return self.parse_response(resp, ViewResponse)

    def get_views(self, **kwargs) -> Response:
        """List all views defined in the system.

        Args:
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_read_metadata_views

        Returns:
            Response: List of metadata views

        Raises:
            - 400 Bad request
            - 401 Token is invalid
        """
        resp = self._get(VIEWS_BASE, **kwargs)
        return self.parse_response(resp, ViewListResponse)

    def get_view(self, view_id: str, merge_fields: bool = None, **kwargs) -> Response:
        """Get a specific view from Iconik.

        Args:
            view_id: ID of the view to retrieve
            merge_fields: Optional boolean to control field merging
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_read_metadata_views

        Returns:
            Response: The requested view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        params = {}
        if merge_fields is not None:
            params["merge_fields"] = merge_fields

        resp = self._get(GET_VIEW_PATH.format(view_id=view_id), params=params, **kwargs)
        return self.parse_response(resp, ViewResponse)

    def delete_view(self, view_id: str, **kwargs) -> Response:
        """Delete a view from Iconik.

        Args:
            view_id: ID of the view to delete
            **kwargs: Additional kwargs to pass to the request

        Required roles:
            - can_delete_metadata_views

        Returns:
            Response: Empty response with 204 status code

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        resp = self._delete(DELETE_VIEW_PATH.format(view_id=view_id), **kwargs)
        return self.parse_response(resp, None)
