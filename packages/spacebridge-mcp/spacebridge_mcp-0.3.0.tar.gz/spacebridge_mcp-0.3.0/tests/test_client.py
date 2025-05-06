import pytest
import os
import json
from unittest.mock import patch, Mock, MagicMock
import requests  # Import requests for exception types

from spacebridge_mcp.spacebridge_client import SpaceBridgeClient
from tests.conftest import MOCK_API_URL, MOCK_API_KEY # Import constants from conftest

# Tests will use the MOCK_API_URL imported from conftest for base URL.
# Constants MOCK_API_URL and MOCK_API_KEY are sourced from conftest.py via the mock_env_vars fixture.

@pytest.fixture(
    params=[
        {"org": None, "project": None},
        {"org": "test-org", "project": "test-project"},
    ]
)
def client_config(request):
    """Provides client configuration parameters (with and without org/project)."""
    return request.param

@pytest.fixture
def client(monkeypatch, client_config):
    """Fixture to create a SpaceBridgeClient with optional org/project.
    Relies on mock_env_vars in conftest.py to set API_URL and API_KEY env vars."""
    # Environment variables are handled by mock_env_vars in conftest.py
    return SpaceBridgeClient(
        org_name=client_config["org"], project_name=client_config["project"]
    )

# Helper to create mock requests.Response
def create_mock_response(status_code, json_data=None, text_data="", raise_for_status_error=None, url="mock://mock_url"):
    """Creates a mock requests.Response object."""
    mock_resp = Mock(spec=requests.Response)
    mock_resp.status_code = status_code
    mock_resp.json = Mock(return_value=json_data if json_data is not None else {})
    mock_resp.text = text_data
    mock_resp.url = url # Set the URL

    # Create a mock request object and attach it
    mock_req = Mock()
    mock_req.url = url
    mock_resp.request = mock_req

    if raise_for_status_error:
        # Attach the response to the error if it's an HTTPError instance
        if isinstance(raise_for_status_error, requests.exceptions.HTTPError):
             raise_for_status_error.response = mock_resp
             raise_for_status_error.request = mock_req # Also attach request to error
        mock_resp.raise_for_status = Mock(side_effect=raise_for_status_error)
    else:
        mock_resp.raise_for_status = Mock() # No error

    mock_resp.headers = {'Content-Type': 'application/json'}
    return mock_resp

@patch('requests.Session.request')
def test_get_issue_success(
    mock_request: MagicMock, client: SpaceBridgeClient, get_issue_test_id: str
):
    """Test successful retrieval of an issue."""
    issue_id = get_issue_test_id
    expected_data = {
        "id": issue_id,
        "title": "Test Issue",
        "status": "Open",
    }

    # Configure mock for non-live tests
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues/{issue_id}" # Use client.api_url which is base
        mock_request.return_value = create_mock_response(200, json_data=expected_data, url=expected_url)

    # Call client method
    issue = client.get_issue(issue_id) # Pass issue_id as 'issue'

    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        # Live test assertions
        assert isinstance(issue, dict)
        assert issue.get("id") == issue_id
        assert "title" in issue
        assert "status" in issue
    else:
        # Mock test assertions
        assert issue == expected_data
        # Verify the mock call - Client's _request calls session.request with relative endpoint
        relative_endpoint = f"issues/{issue_id}"
        mock_request.assert_called_once_with(
            "GET",
            relative_endpoint, # Assert relative endpoint
            headers=client.headers,
            params=None,
            json=None,
        )

@patch('requests.Session.request')
def test_get_issue_not_found(mock_request: MagicMock, client: SpaceBridgeClient):
    """Test handling of 404 error when getting an issue."""
    issue_id = "NON-EXISTENT-ID-12345"

    # Configure mock for non-live tests
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues/{issue_id}" # Full URL for context
        relative_endpoint = f"issues/{issue_id}" # Relative path for assertion

        # Simulate HTTPError on raise_for_status
        http_error = requests.exceptions.HTTPError(f"404 Client Error for url: {expected_url}")
        # create_mock_response will attach the response and request to the error
        mock_request.return_value = create_mock_response(
            404, raise_for_status_error=http_error, url=expected_url
        )

    # Expect requests.exceptions.HTTPError
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        client.get_issue(issue_id) # Pass issue_id as 'issue'

    # Verify mock call in non-live mode
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        relative_endpoint = f"issues/{issue_id}"
        mock_request.assert_called_once_with(
            "GET",
            relative_endpoint, # Assert relative endpoint
            headers=client.headers,
            params=None,
            json=None,
        )
        # Assert on the response attached to the exception
        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 404
        assert excinfo.value.response.url == expected_url


@pytest.mark.parametrize(
    "call_context",
    [
        {},
        {"org": "call_org", "project": "call_proj"},
        {"org": "call_org", "project": None},
        {"org": None, "project": "call_proj"},
    ],
)
@patch('requests.Session.request')
def test_search_issues_success(
    mock_request: MagicMock, client: SpaceBridgeClient, client_config, call_context
):
    """Test successful search, checking client startup vs explicit call context."""
    query = "bug fix"
    search_type = "full_text"
    # New optional filter params for search
    status_filter = "Open"
    labels_filter = ["bug", "ui"]
    assignee_filter = "dev1"
    priority_filter = "High"

    expected_results = [
        {"id": "SB-1", "title": "Fix login bug"},
        {"id": "SB-2", "title": "Bug in search results"},
    ]

    # Determine the context expected in the API call params
    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        final_org = "spagent"
        final_project = "agentplayground"
        call_org_name = "spagent"
        call_project_name = "agentplayground"
    else:
        final_org = call_context.get("org") if call_context.get("org") is not None else client_config.get("org")
        final_project = call_context.get("project") if call_context.get("project") is not None else client_config.get("project")
        call_org_name = call_context.get("org")
        call_project_name = call_context.get("project")

    # Prepare expected parameters for the mock verification
    expected_params = {
        "query": query,
        "search_type": search_type,
        "status": status_filter,
        "labels": ",".join(labels_filter) if labels_filter else None, # API expects comma-separated string
        "assignee": assignee_filter,
        "priority": priority_filter,
    }
    if final_org:
        expected_params["organization"] = final_org
    if final_project:
        expected_params["project"] = final_project

    # Configure mock for non-live tests
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues/search" # Base URL for client method
        mock_request.return_value = create_mock_response(200, json_data=expected_results, url=expected_url) # Mock uses full URL

    # Call the client method with explicit args and new filters
    results = client.search_issues(
        query=query,
        search_type=search_type,
        org_name=call_org_name,
        project_name=call_project_name,
        status=status_filter,
        labels=labels_filter, # Pass list directly
        assignee=assignee_filter,
        priority=priority_filter,
    )

    # Assertions
    assert results == expected_results

    # Verify the API call used the correctly prioritized context and filters
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        # Filter out None values from expected_params for comparison
        expected_params_filtered = {k: v for k, v in expected_params.items() if v is not None}
        # Client's _request calls session.request with relative endpoint
        relative_endpoint = "issues/search"
        mock_request.assert_called_once_with(
            "GET",
            relative_endpoint, # Assert relative endpoint
            headers=client.headers,
            params=expected_params_filtered, # Pass the filtered params dict
            json=None,
        )

@pytest.mark.parametrize(
    "call_context",
    [
        {},
        {"org": "call_org", "project": "call_proj"},
    ],
)
@patch('requests.Session.request')
def test_search_issues_similarity_success(
    mock_request: MagicMock, client: SpaceBridgeClient, client_config, call_context
):
    """Test successful similarity search, checking context priority."""
    query = "similar bug"
    search_type = "similarity"
    expected_results = [
        {"id": "SB-1", "title": "Fix login bug", "score": 0.9},
    ]

    # Determine expected context (logic remains the same as previous test)
    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        final_org = "spagent"
        final_project = "agentplayground"
        call_org_name = "spagent"
        call_project_name = "agentplayground"
    else:
        final_org = call_context.get("org") if call_context.get("org") is not None else client_config.get("org")
        final_project = call_context.get("project") if call_context.get("project") is not None else client_config.get("project")
        call_org_name = call_context.get("org")
        call_project_name = call_context.get("project")

    # Prepare expected parameters (no filters in this specific test case)
    expected_params = {"query": query, "search_type": search_type}
    if final_org:
        expected_params["organization"] = final_org
    if final_project:
        expected_params["project"] = final_project
    # Add None for new filters as they are not used here
    expected_params["status"] = None
    expected_params["labels"] = None
    expected_params["assignee"] = None
    expected_params["priority"] = None


    # Configure mock for non-live tests
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues/search" # Base URL for client method
        mock_request.return_value = create_mock_response(200, json_data=expected_results, url=expected_url) # Mock uses full URL

    # Call client method (without new filters)
    results = client.search_issues(
        query=query,
        search_type=search_type,
        org_name=call_org_name,
        project_name=call_project_name,
        # Omitting status, labels, assignee, priority
    )

    # Assertions
    assert results == expected_results

    # Verify the API call
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_params_filtered = {k: v for k, v in expected_params.items() if v is not None}
        # Client's _request calls session.request with relative endpoint
        relative_endpoint = "issues/search"
        mock_request.assert_called_once_with(
            "GET",
            relative_endpoint, # Assert relative endpoint
            headers=client.headers,
            params=expected_params_filtered,
            json=None,
        )

@pytest.mark.parametrize(
    "call_context",
    [
        {},
        {"org": "call_org", "project": "call_proj"},
    ],
)
@patch('requests.Session.request')
def test_create_issue_success(
    mock_request: MagicMock, client: SpaceBridgeClient, client_config, call_context
):
    """Test successful creation, checking context priority."""
    title = "New Feature"
    description = "Add dark mode"
    labels = ["feature", "ui"] # Add labels for testing
    expected_response = {
        "id": "SB-NEW",
        "title": title,
        "description": description,
        "labels": labels,
        "status": "New",
    }

    # Determine expected context (logic remains the same)
    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        final_org = "spagent"
        final_project = "agentplayground"
        call_org_name = "spagent"
        call_project_name = "agentplayground"
    else:
        final_org = call_context.get("org") if call_context.get("org") is not None else client_config.get("org")
        final_project = call_context.get("project") if call_context.get("project") is not None else client_config.get("project")
        call_org_name = call_context.get("org")
        call_project_name = call_context.get("project")

    # Prepare expected payload
    expected_payload = {"title": title, "description": description, "labels": labels} # Include labels
    if final_org:
        expected_payload["organization"] = final_org
    if final_project:
        expected_payload["project"] = final_project

    # Configure mock for non-live tests
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues" # Base URL for client method
        mock_request.return_value = create_mock_response(201, json_data=expected_response, url=expected_url) # Mock uses full URL

    # Call the client method
    # Expect ValueError only if project context is missing
    if final_project is None and os.getenv("RUN_LIVE_API_TESTS") != "1": # Check only needed for mock tests
         with pytest.raises(ValueError, match="Project name is required to create an issue."):
             client.create_issue(
                 title=title,
                 description=description,
                 labels=labels, # Pass labels
                 org_name=call_org_name,
                 project_name=call_project_name,
             )
    else:
        new_issue = client.create_issue(
            title=title,
            description=description,
            labels=labels, # Pass labels
            org_name=call_org_name,
            project_name=call_project_name,
        )
        # Assertion
        assert new_issue == expected_response

        # Verify the request payload was correct
        if os.getenv("RUN_LIVE_API_TESTS") != "1":
            # Client's _request calls session.request with relative endpoint
            relative_endpoint = "issues"
            mock_request.assert_called_once_with(
                "POST",
                relative_endpoint, # Assert relative endpoint
                headers=client.headers,
                params=None,
                json=expected_payload,
            )

# Test client initialization - these don't need mocking changes
def test_client_init_missing_url(monkeypatch):
    """Test client initialization uses default URL if env var is missing."""
    default_url = "https://spacebridge.io" # Default URL before /api/v1 is handled by session
    monkeypatch.delenv("SPACEBRIDGE_API_URL", raising=False)
    monkeypatch.setenv("SPACEBRIDGE_API_KEY", MOCK_API_KEY)
    client = SpaceBridgeClient()
    assert client.api_url == default_url # Assert against the base URL

def test_client_init_missing_key(monkeypatch):
    """Test client initialization fails if API key is missing."""
    monkeypatch.setenv("SPACEBRIDGE_API_URL", MOCK_API_URL)
    monkeypatch.delenv("SPACEBRIDGE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API Key not configured"):
        SpaceBridgeClient()

@pytest.mark.parametrize(
    "call_context",
    [
        {},
        {"org": "call_org", "project": "call_proj"},
    ],
)
@patch('requests.Session.request')
def test_update_issue_success(
    mock_request: MagicMock, client: SpaceBridgeClient, client_config, call_context, update_issue_test_id: str
):
    """Test successful update, checking context priority."""
    issue_id = update_issue_test_id
    update_data = {
        "status": "In Progress",
        "title": "Updated Title via Test",
        "labels": ["bug", "regression"], # Add labels update
        "priority": "High", # Add priority update
    }
    # Mock response structure
    expected_response = {
        "id": issue_id,
        "title": update_data["title"],
        "description": "Existing Desc", # Assuming description is not updated
        "status": update_data["status"],
        "labels": update_data["labels"],
        "priority": update_data["priority"],
    }

    # Determine expected context (logic remains the same)
    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        final_org = "spagent"
        final_project = "agentplayground"
        call_org_name = "spagent"
        call_project_name = "agentplayground"
    else:
        final_org = call_context.get("org") if call_context.get("org") is not None else client_config.get("org")
        final_project = call_context.get("project") if call_context.get("project") is not None else client_config.get("project")
        call_org_name = call_context.get("org")
        call_project_name = call_context.get("project")


    # Prepare expected payload
    expected_payload = update_data.copy() # Start with actual update fields
    if final_org:
        expected_payload["organization"] = final_org
    if final_project:
        expected_payload["project"] = final_project

    # Mock the API call
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        expected_url = f"{client.api_url}/issues/{issue_id}" # Base URL for client method
        mock_request.return_value = create_mock_response(200, json_data=expected_response, url=expected_url) # Mock uses full URL

    # Call client method
    updated_issue = client.update_issue(
        issue=issue_id, # Use 'issue' instead of 'issue_id'
        org_name=call_org_name,
        project_name=call_project_name,
        **update_data, # Pass update fields as kwargs
    )

    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        # Live Assertions
        assert isinstance(updated_issue, dict)
        assert updated_issue.get("id") == issue_id
        assert updated_issue.get("status") == update_data["status"]
        assert updated_issue.get("title") == update_data["title"]
        # Check potentially updated fields (API might not return all)
        if "labels" in updated_issue:
             assert sorted(updated_issue.get("labels")) == sorted(update_data["labels"])
        if "priority" in updated_issue:
             assert updated_issue.get("priority") == update_data["priority"]
    else:
        # Mock Assertions
        assert updated_issue == expected_response

        # Verify the request payload was correct
        # Client's _request calls session.request with relative endpoint
        relative_endpoint = f"issues/{issue_id}"
        mock_request.assert_called_once_with(
            "PUT",
            relative_endpoint, # Assert relative endpoint
            headers=client.headers,
            params=None,
            json=expected_payload,
        )

# This test doesn't make an HTTP call, so no mocking changes needed
@patch('requests.Session.request') # Add patch for consistency, though it shouldn't be called
def test_update_issue_no_fields(mock_request: MagicMock, client: SpaceBridgeClient):
    """Test calling update_issue with no fields to update."""
    issue_id = "SB-NOUPDATE"

    # Call update with no keyword arguments for update fields
    result = client.update_issue(issue=issue_id) # Use 'issue' instead of 'issue_id'

    # Check the minimal response returned by the client method
    assert result == {"id": issue_id, "message": "No fields provided for update."}

    # Ensure no HTTP call was made
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        mock_request.assert_not_called()
