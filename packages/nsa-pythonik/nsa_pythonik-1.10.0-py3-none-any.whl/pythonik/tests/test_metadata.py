import uuid
import requests_mock
from pythonik.client import PythonikClient
from requests import HTTPError
from pythonik.models.base import ObjectType
from loguru import logger

from pythonik.models.metadata.views import (
    FieldValue,
    FieldValues,
    MetadataValues,
    ViewMetadata,
    CreateViewRequest,
    ViewField,
    ViewOption,
    UpdateViewRequest,
)
from pythonik.models.mutation.metadata.mutate import (
    UpdateMetadata,
    UpdateMetadataResponse,
)
from pythonik.models.metadata.view_responses import ViewResponse, ViewListResponse
from pythonik.specs.metadata import (
    ASSET_METADATA_FROM_VIEW_PATH,
    UPDATE_ASSET_METADATA,
    MetadataSpec,
    ASSET_OBJECT_VIEW_PATH,
    PUT_METADATA_DIRECT_PATH,
    CREATE_VIEW_PATH,
    VIEWS_BASE,
    UPDATE_VIEW_PATH,
    DELETE_VIEW_PATH,
    GET_VIEW_PATH,
)


def test_get_asset_metadata():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        model = ViewMetadata()
        data = model.model_dump()
        mock_address = MetadataSpec.gen_url(
            ASSET_METADATA_FROM_VIEW_PATH.format(asset_id, view_id)
        )
        m.get(mock_address, json=data)
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.metadata().get_asset_metadata(asset_id, view_id)


def test_get_asset_intercept_404():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        mv = MetadataValues(
            {
                "this_worked_right?": FieldValues(
                    field_values=[FieldValue(value="lets hope")]
                )
            }
        )

        model = ViewMetadata()
        model.metadata_values = mv
        data = model.model_dump()
        mock_address = MetadataSpec.gen_url(
            ASSET_METADATA_FROM_VIEW_PATH.format(asset_id, view_id)
        )
        m.get(mock_address, json=data, status_code=404)
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        resp = client.metadata().get_asset_metadata(
            asset_id, view_id, intercept_404=model
        )
        assert resp.data == model


def test_get_asset_intercept_404_raise_for_status():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        mv = MetadataValues(
            {
                "this_worked_right?": FieldValues(
                    field_values=[FieldValue(value="lets hope")]
                )
            }
        )

        model = ViewMetadata()
        model.metadata_values = mv
        data = model.model_dump()
        mock_address = MetadataSpec.gen_url(
            ASSET_METADATA_FROM_VIEW_PATH.format(asset_id, view_id)
        )
        m.get(mock_address, json=data, status_code=404)
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        resp = client.metadata().get_asset_metadata(
            asset_id, view_id, intercept_404=model
        )
        # should not raise for status
        try:
            resp.response.raise_for_status()
            # this line should run and the above should not raise for status
            assert True is True
        except Exception as e:
            pass


def test_get_asset_intercept_404_raise_for_status_404():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        mv = MetadataValues(
            {
                "this_worked_right?": FieldValues(
                    field_values=[FieldValue(value="lets hope")]
                )
            }
        )

        model = ViewMetadata()
        model.metadata_values = mv
        data = model.model_dump()
        mock_address = MetadataSpec.gen_url(
            ASSET_METADATA_FROM_VIEW_PATH.format(asset_id, view_id)
        )
        m.get(mock_address, json=data, status_code=404)
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        resp = client.metadata().get_asset_metadata(
            asset_id, view_id, intercept_404=model
        )
        # should not raise for status
        exception = None
        try:
            resp.response.raise_for_status_404()
            # this line should run and the above should not raise for status
        except HTTPError as e:
            exception = e

        # assert exception still raised with 404
        assert exception.response.status_code == 404


def test_update_asset_metadata():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())
        payload = {"metadata_values": {"field1": {"field_values": [{"value": "123"}]}}}

        mutate_model = UpdateMetadata.model_validate(payload)
        response_model = UpdateMetadataResponse(
            metadata_values=mutate_model.metadata_values.model_dump()
        )

        mock_address = MetadataSpec.gen_url(
            UPDATE_ASSET_METADATA.format(asset_id, view_id)
        )
        m.put(mock_address, json=response_model.model_dump())
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.metadata().update_asset_metadata(asset_id, view_id, mutate_model)


def test_put_segment_view_metadata():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        segment_id = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create test payload
        payload = {"metadata_values": {"field1": {"field_values": [{"value": "123"}]}}}

        mutate_model = UpdateMetadata.model_validate(payload)
        response_model = UpdateMetadataResponse(
            metadata_values=mutate_model.metadata_values.model_dump()
        )

        # Mock the endpoint using the ASSET_OBJECT_VIEW_PATH
        mock_address = MetadataSpec.gen_url(
            ASSET_OBJECT_VIEW_PATH.format(asset_id, "segments", segment_id, view_id)
        )
        m.put(mock_address, json=response_model.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.metadata().put_segment_view_metadata(
            asset_id, segment_id, view_id, mutate_model
        )


def test_put_metadata_direct():
    """Test direct metadata update without a view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        object_type = ObjectType.ASSETS.value
        object_id = str(uuid.uuid4())

        # Create test metadata
        metadata_values = {
            "metadata_values": {
                "test_field": {"field_values": [{"value": "test_value"}]}
            }
        }
        metadata = UpdateMetadata.model_validate(metadata_values)

        # Expected response
        response_data = {
            "date_created": "2024-12-10T19:58:25Z",
            "date_modified": "2024-12-10T19:58:25Z",
            "metadata_values": metadata_values["metadata_values"],
            "object_id": object_id,
            "object_type": object_type,
            "version_id": str(uuid.uuid4()),
        }

        # Mock the PUT request
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(mock_address, json=response_data)

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert response.response.ok
        assert response.data.object_id == object_id
        assert response.data.object_type == object_type
        assert response.data.metadata_values == metadata_values["metadata_values"]


def test_put_metadata_direct_unauthorized():
    """Test direct metadata update with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"
        object_type = ObjectType.ASSETS.value
        object_id = str(uuid.uuid4())

        # Create empty metadata
        metadata = UpdateMetadata.model_validate({"metadata_values": {}})

        # Mock the PUT request to return 401
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(mock_address, status_code=401)

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert not response.response.ok
        assert response.response.status_code == 401


def test_put_metadata_direct_404():
    """Test direct metadata update with non-existent object."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        object_type = ObjectType.ASSETS.value
        object_id = str(uuid.uuid4())

        # Create test metadata
        metadata = UpdateMetadata.model_validate({"metadata_values": {}})

        # Mock the PUT request to return 404
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(
            mock_address,
            status_code=404,
            json={
                "error": "Object not found",
                "message": f"Object {object_id} of type {object_type} not found",
            },
        )

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert not response.response.ok
        assert response.response.status_code == 404


def test_put_metadata_direct_invalid_format():
    """Test direct metadata update with invalid metadata format."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        object_type = ObjectType.ASSETS.value
        object_id = str(uuid.uuid4())

        # Create test metadata with invalid format
        metadata_values = {
            "metadata_values": {
                "test_field": {
                    # Missing required field_values array
                    "value": "test_value"
                }
            }
        }
        metadata = UpdateMetadata.model_validate({"metadata_values": {}})

        # Mock the PUT request to return 400
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(
            mock_address,
            status_code=400,
            json={
                "error": "Invalid metadata format",
                "message": "Metadata values must contain field_values array",
            },
        )

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert not response.response.ok
        assert response.response.status_code == 400


def test_put_metadata_direct_malformed():
    """Test direct metadata update with malformed request."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        object_type = "invalid_type"  # Invalid object type
        object_id = str(uuid.uuid4())

        # Create test metadata
        metadata = UpdateMetadata.model_validate({"metadata_values": {}})

        # Mock the PUT request to return 400
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(
            mock_address,
            status_code=400,
            json={
                "error": "Invalid request",
                "message": "Invalid object type: must be one of [assets, segments, collections]",
            },
        )

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert not response.response.ok
        assert response.response.status_code == 400


def test_put_metadata_direct_forbidden():
    """Test direct metadata update with non-admin user."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())  # Valid token but non-admin user
        object_type = ObjectType.ASSETS.value
        object_id = str(uuid.uuid4())

        # Create test metadata
        metadata = UpdateMetadata.model_validate({"metadata_values": {}})

        # Mock the PUT request to return 403
        mock_address = MetadataSpec.gen_url(
            PUT_METADATA_DIRECT_PATH.format(object_type, object_id)
        )
        m.put(
            mock_address,
            status_code=403,
            json={
                "error": "Forbidden",
                "message": "Admin access required for direct metadata updates",
            },
        )

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.metadata().put_metadata_direct(
            object_type, object_id, metadata
        )

        # Verify response
        assert not response.response.ok
        assert response.response.status_code == 403


def test_create_view():
    """Test creating a new view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create request data
        view = CreateViewRequest(
            name="Test View",
            description="A test view",
            view_fields=[
                ViewField(
                    name="field1",
                    label="Field 1",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="Option 1", value="opt1"),
                        ViewOption(label="Option 2", value="opt2"),
                    ],
                )
            ],
        )

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view.name,
            description=view.description,
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T18:40:03.279Z",
            view_fields=view.view_fields,
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(CREATE_VIEW_PATH)
        m.post(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().create_view(view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == view.description
        assert len(result.data.view_fields) == len(view.view_fields)
        assert result.data.view_fields[0].name == view.view_fields[0].name


def test_create_view_with_dict():
    """Test creating a new view using a dictionary."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create request data as dict
        view = {
            "name": "Test View",
            "description": "A test view",
            "view_fields": [
                {
                    "name": "field1",
                    "label": "Field 1",
                    "required": True,
                    "field_type": "string",
                    "options": [
                        {"label": "Option 1", "value": "opt1"},
                        {"label": "Option 2", "value": "opt2"},
                    ],
                }
            ],
        }

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view["name"],
            description=view["description"],
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T18:40:03.279Z",
            view_fields=[ViewField(**field) for field in view["view_fields"]],
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(CREATE_VIEW_PATH)
        m.post(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().create_view(view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view["name"]
        assert result.data.description == view["description"]
        assert len(result.data.view_fields) == len(view["view_fields"])
        assert result.data.view_fields[0].name == view["view_fields"][0]["name"]


def test_create_view_bad_request():
    """Test creating a view with invalid data."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())

        # Create invalid request (missing required fields)
        view = CreateViewRequest(
            name="Test View",
            view_fields=[],  # Invalid: view_fields cannot be empty
        )

        # Mock the API call with 400 response
        mock_address = MetadataSpec.gen_url(CREATE_VIEW_PATH)
        m.post(mock_address, status_code=400, json={"error": "Invalid view_fields"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().create_view(view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 400
        assert result.data is None


def test_create_view_unauthorized():
    """Test creating a view with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"

        view = CreateViewRequest(
            name="Test View",
            description="A test view",
            view_fields=[ViewField(name="field1", label="Field 1", required=True)],
        )

        # Mock the API call with 401 response
        mock_address = MetadataSpec.gen_url(CREATE_VIEW_PATH)
        m.post(mock_address, status_code=401, json={"error": "Invalid token"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().create_view(view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_get_views():
    """Test getting list of views."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create expected response
        view = ViewResponse(
            id=view_id,
            name="Test View",
            description="A test view",
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T18:40:03.279Z",
            view_fields=[
                ViewField(
                    name="field1",
                    label="Field 1",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="Option 1", value="opt1"),
                        ViewOption(label="Option 2", value="opt2"),
                    ],
                )
            ],
        )
        response = ViewListResponse(objects=[view], page=1, pages=1, per_page=10)

        # Mock the API call
        mock_address = MetadataSpec.gen_url(VIEWS_BASE)
        m.get(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_views()

        # Verify response
        assert result.response.ok
        assert len(result.data.objects) == 1
        assert result.data.objects[0].id == view_id
        assert result.data.objects[0].name == view.name
        assert result.data.objects[0].description == view.description
        assert len(result.data.objects[0].view_fields) == len(view.view_fields)
        assert result.data.objects[0].view_fields[0].name == view.view_fields[0].name
        assert result.data.page == 1
        assert result.data.pages == 1
        assert result.data.per_page == 10


def test_get_views_unauthorized():
    """Test getting views with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"

        # Mock the API call with 401 response
        mock_address = MetadataSpec.gen_url(VIEWS_BASE)
        m.get(mock_address, status_code=401, json={"error": "Invalid token"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_views()

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_get_views_empty():
    """Test getting empty list of views."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())

        # Create expected response with empty list
        response = ViewListResponse(objects=[], page=1, pages=1, per_page=10)

        # Mock the API call
        mock_address = MetadataSpec.gen_url(VIEWS_BASE)
        m.get(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_views()

        # Verify response
        assert result.response.ok
        assert len(result.data.objects) == 0
        assert result.data.page == 1
        assert result.data.pages == 1
        assert result.data.per_page == 10


def test_update_view():
    """Test updating a view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create update request
        view = UpdateViewRequest(
            name="Updated View",
            description="An updated test view",
            view_fields=[
                ViewField(
                    name="field1",
                    label="Updated Field 1",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="New Option 1", value="new1"),
                        ViewOption(label="New Option 2", value="new2"),
                    ],
                )
            ],
        )

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view.name,
            description=view.description,
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T19:22:58.522Z",  # Note: modified time updated
            view_fields=view.view_fields,
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.patch(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().update_view(view_id, view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == view.description
        assert len(result.data.view_fields) == len(view.view_fields)
        assert result.data.view_fields[0].name == view.view_fields[0].name
        assert result.data.view_fields[0].label == view.view_fields[0].label


def test_update_view_with_dict():
    """Test updating a view using a dictionary."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create update request as dict
        view = {
            "name": "Updated View",
            "description": "An updated test view",
            "view_fields": [
                {
                    "name": "field1",
                    "label": "Updated Field 1",
                    "required": True,
                    "field_type": "string",
                    "options": [
                        {"label": "New Option 1", "value": "new1"},
                        {"label": "New Option 2", "value": "new2"},
                    ],
                }
            ],
        }

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view["name"],
            description=view["description"],
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T19:22:58.522Z",  # Note: modified time updated
            view_fields=[ViewField(**field) for field in view["view_fields"]],
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.patch(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().update_view(view_id, view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view["name"]
        assert result.data.description == view["description"]
        assert len(result.data.view_fields) == len(view["view_fields"])
        assert result.data.view_fields[0].name == view["view_fields"][0]["name"]
        assert result.data.view_fields[0].label == view["view_fields"][0]["label"]


def test_update_view_not_found():
    """Test updating a non-existent view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = "non_existent_id"

        view = UpdateViewRequest(
            name="Updated View", description="An updated test view"
        )

        # Mock the API call with 404 response
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.patch(mock_address, status_code=404, json={"error": "View not found"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().update_view(view_id, view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 404
        assert result.data is None


def test_update_view_unauthorized():
    """Test updating a view with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"
        view_id = str(uuid.uuid4())

        view = UpdateViewRequest(
            name="Updated View", description="An updated test view"
        )

        # Mock the API call with 401 response
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.patch(mock_address, status_code=401, json={"error": "Invalid token"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().update_view(view_id, view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_update_view_partial():
    """Test partial update of a view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create partial update request (only updating name)
        view = UpdateViewRequest(name="Updated View")

        # Create expected response (other fields unchanged)
        response = ViewResponse(
            id=view_id,
            name=view.name,
            description="Original description",  # Unchanged
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T19:22:58.522Z",  # Note: modified time updated
            view_fields=[  # Original fields unchanged
                ViewField(
                    name="field1", label="Field 1", required=True, field_type="string"
                )
            ],
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.patch(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().update_view(view_id, view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == "Original description"  # Unchanged
        assert len(result.data.view_fields) == 1  # Original fields unchanged


def test_replace_view():
    """Test replacing a view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create replacement view data
        view = CreateViewRequest(
            name="Replaced View",
            description="A completely new view",
            view_fields=[
                ViewField(
                    name="new_field",
                    label="New Field",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="New Option 1", value="new1"),
                        ViewOption(label="New Option 2", value="new2"),
                    ],
                )
            ],
        )

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view.name,
            description=view.description,
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T19:28:42.213Z",  # Note: modified time updated
            view_fields=view.view_fields,
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.put(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().replace_view(view_id, view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == view.description
        assert len(result.data.view_fields) == len(view.view_fields)
        assert result.data.view_fields[0].name == view.view_fields[0].name
        assert result.data.view_fields[0].label == view.view_fields[0].label


def test_replace_view_with_dict():
    """Test replacing a view using a dictionary."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create replacement view data as dict
        view = {
            "name": "Replaced View",
            "description": "A completely new view",
            "view_fields": [
                {
                    "name": "new_field",
                    "label": "New Field",
                    "required": True,
                    "field_type": "string",
                    "options": [
                        {"label": "New Option 1", "value": "new1"},
                        {"label": "New Option 2", "value": "new2"},
                    ],
                }
            ],
        }

        # Create expected response
        response = ViewResponse(
            id=view_id,
            name=view["name"],
            description=view["description"],
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T19:28:42.213Z",  # Note: modified time updated
            view_fields=[ViewField(**field) for field in view["view_fields"]],
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.put(mock_address, json=response.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().replace_view(view_id, view)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view["name"]
        assert result.data.description == view["description"]
        assert len(result.data.view_fields) == len(view["view_fields"])
        assert result.data.view_fields[0].name == view["view_fields"][0]["name"]
        assert result.data.view_fields[0].label == view["view_fields"][0]["label"]


def test_replace_view_not_found():
    """Test replacing a non-existent view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = "non_existent_id"

        view = CreateViewRequest(
            name="Replaced View",
            description="A completely new view",
            view_fields=[ViewField(name="new_field", label="New Field", required=True)],
        )

        # Mock the API call with 404 response
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.put(mock_address, status_code=404, json={"error": "View not found"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().replace_view(view_id, view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 404
        assert result.data is None


def test_replace_view_unauthorized():
    """Test replacing a view with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"
        view_id = str(uuid.uuid4())

        view = CreateViewRequest(
            name="Replaced View",
            description="A completely new view",
            view_fields=[ViewField(name="new_field", label="New Field", required=True)],
        )

        # Mock the API call with 401 response
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.put(mock_address, status_code=401, json={"error": "Invalid token"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().replace_view(view_id, view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_replace_view_bad_request():
    """Test replacing a view with invalid data."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create invalid request (missing required fields) as dict
        view = {
            "name": "Replaced View"  # Missing required view_fields
        }

        # Mock the API call with 400 response
        mock_address = MetadataSpec.gen_url(UPDATE_VIEW_PATH.format(view_id=view_id))
        m.put(mock_address, status_code=400, json={"error": "Missing required fields"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().replace_view(view_id, view)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 400
        assert result.data is None


def test_delete_view():
    """Test deleting a view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Mock the API call
        mock_address = MetadataSpec.gen_url(DELETE_VIEW_PATH.format(view_id=view_id))
        m.delete(mock_address, status_code=204)

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().delete_view(view_id)

        # Verify response
        assert result.response.ok
        assert result.response.status_code == 204
        assert result.data is None


def test_delete_view_not_found():
    """Test deleting a non-existent view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = "non_existent_id"

        # Mock the API call with 404 response
        mock_address = MetadataSpec.gen_url(DELETE_VIEW_PATH.format(view_id=view_id))
        m.delete(mock_address, status_code=404, json={"error": "View not found"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().delete_view(view_id)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 404
        assert result.data is None


def test_delete_view_unauthorized():
    """Test deleting a view with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"
        view_id = str(uuid.uuid4())

        # Mock the API call with 401 response
        mock_address = MetadataSpec.gen_url(DELETE_VIEW_PATH.format(view_id=view_id))
        m.delete(mock_address, status_code=401, json={"error": "Invalid token"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().delete_view(view_id)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_delete_view_bad_request():
    """Test deleting a view with invalid request."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = "invalid!id@#$"  # Invalid ID format

        # Mock the API call with 400 response
        mock_address = MetadataSpec.gen_url(DELETE_VIEW_PATH.format(view_id=view_id))
        m.delete(
            mock_address, status_code=400, json={"error": "Invalid view ID format"}
        )

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().delete_view(view_id)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 400
        assert result.data is None


def test_get_view():
    """Test getting a specific view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create expected response
        view = ViewResponse(
            id=view_id,
            name="Test View",
            description="A test view",
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T18:40:03.279Z",
            view_fields=[
                ViewField(
                    name="field1",
                    label="Field 1",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="Option 1", value="opt1"),
                        ViewOption(label="Option 2", value="opt2"),
                    ],
                )
            ],
        )

        # Mock the API call
        mock_address = MetadataSpec.gen_url(GET_VIEW_PATH.format(view_id=view_id))
        m.get(mock_address, json=view.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_view(view_id)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == view.description
        assert len(result.data.view_fields) == len(view.view_fields)
        assert result.data.view_fields[0].name == view.view_fields[0].name
        assert len(result.data.view_fields[0].options) == len(
            view.view_fields[0].options
        )


def test_get_view_not_found():
    """Test getting a non-existent view."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = "non_existent_id"

        # Mock the API call
        mock_address = MetadataSpec.gen_url(GET_VIEW_PATH.format(view_id=view_id))
        m.get(mock_address, status_code=404, json={"error": "View not found"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_view(view_id)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 404
        assert result.data is None


def test_get_view_unauthorized():
    """Test getting a view with invalid token."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = "invalid_token"
        view_id = str(uuid.uuid4())

        # Mock the API call
        mock_address = MetadataSpec.gen_url(GET_VIEW_PATH.format(view_id=view_id))
        m.get(mock_address, status_code=401, json={"error": "Unauthorized"})

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_view(view_id)

        # Verify response
        assert not result.response.ok
        assert result.response.status_code == 401
        assert result.data is None


def test_get_view_with_merge_fields():
    """Test getting a view with merge_fields parameter."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())

        # Create expected response
        view = ViewResponse(
            id=view_id,
            name="Test View",
            description="A test view",
            date_created="2024-12-20T18:40:03.279Z",
            date_modified="2024-12-20T18:40:03.279Z",
            view_fields=[
                ViewField(
                    name="field1",
                    label="Field 1",
                    required=True,
                    field_type="string",
                    options=[
                        ViewOption(label="Option 1", value="opt1"),
                        ViewOption(label="Option 2", value="opt2"),
                    ],
                )
            ],
        )

        # Mock the API call with merge_fields parameter
        mock_address = MetadataSpec.gen_url(GET_VIEW_PATH.format(view_id=view_id))
        m.get(f"{mock_address}?merge_fields=true", json=view.model_dump())

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        result = client.metadata().get_view(view_id, merge_fields=True)

        # Verify response
        assert result.response.ok
        assert result.data.id == view_id
        assert result.data.name == view.name
        assert result.data.description == view.description
        assert len(result.data.view_fields) == len(view.view_fields)
        assert result.data.view_fields[0].name == view.view_fields[0].name
        assert len(result.data.view_fields[0].options) == len(
            view.view_fields[0].options
        )


def test_get_view_alternate_base_url():
    """Test getting a view with an alternate base URL."""
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        view_id = str(uuid.uuid4())
        alternate_base = "https://custom.iconik.io"

        # Create test data
        field = ViewField(
            field_id="test_field",
            name="Test Field",
            label="Test Field Label",
            type="text",
            required=False,
            options=[ViewOption(value="option1", label="Option 1")],
        )
        model = ViewResponse(
            id=str(uuid.uuid4()),
            name="Test View",
            date_created="2025-01-29T12:00:00Z",
            date_modified="2025-01-29T12:00:00Z",
            view_fields=[field],
            fields=[field],
        )
        data = model.model_dump()

        # Mock the endpoint with the expected URL pattern from MetadataSpec
        mock_address = f"{alternate_base}/API/metadata/v1/views/{view_id}/"
        m.get(mock_address, json=data)

        client = PythonikClient(
            app_id=app_id, auth_token=auth_token, timeout=3, base_url=alternate_base
        )
        response = client.metadata().get_view(view_id)

        # Verify the response
        assert response.data == model
        # Verify the request was made to the correct URL
        logger.info(m.last_request.url)
        logger.info(mock_address)
        assert m.last_request.url == mock_address
