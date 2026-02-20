import json
import uuid
import mimetypes
from typing import Optional, List, Dict, Any, Union

__all__ = ['get_project_issues', 'get_deleted_issues', 'create_issue']

# Default items per page for paginated endpoints
DEFAULT_PAGE_SIZE = 100

def get_project_issues(
    auth_client: Any,
    project_uuid: str,
    page: int = 0,
    always_filters: Optional[List[Dict[str, Any]]] = None,
    any_filters: Optional[List[Dict[str, Any]]] = None,
    additional_fields: Optional[List[str]] = None,
    report_sort: Optional[List[Dict[str, str]]] = None,
    limit: int = DEFAULT_PAGE_SIZE,
    send_full_issue_data: bool = False,
    synchronized: Optional[str] = None,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Fetch a list of issues for a project, with support for filters, sorting, and pagination.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        page: Page number to retrieve. Defaults to 0.
        always_filters: Filters to always apply.
        any_filters: Filters to optionally apply.
        additional_fields: Additional fields to include in the response.
        report_sort: Sorting parameters.
        limit: Number of issues per page. Defaults to 100.
        send_full_issue_data: Whether to fetch full issue data or only changed fields.
        synchronized: Fetch issues created/updated after a specific time (YYYY-MM-DD HH:MM:SS).

    Returns:
        List or dict containing the fetched issues.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter"
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
        "sendFullIssueData": send_full_issue_data,
        "synchronized": synchronized,
    }

    if additional_fields:
        params["additionalFields[]"] = additional_fields

    if always_filters:
        params["alwaysFiltersDTO[]"] = always_filters

    if any_filters:
        params["anyFiltersDTO[]"] = any_filters

    if report_sort:
        params["reportSort[]"] = report_sort

    return auth_client._request("GET", url, params=params)

def get_deleted_issues(
    auth_client: Any,
    project_uuid: str,
    page: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    additional_fields: Optional[List[str]] = None,
    always_filters_dto: Optional[List[Dict[str, Any]]] = None,
    any_filters_dto: Optional[List[Dict[str, Any]]] = None,
    report_sort: Optional[List[str]] = None,
    send_full_issue_data: bool = False,
    statuses: Optional[List[str]] = None,
    synchronized: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a list of deleted issues with optional filtering and sorting for a specific page.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        page: Page number to retrieve. Defaults to 0.
        limit: Number of issues per page. Defaults to 100.
        additional_fields: Additional fields to include in the response.
        always_filters_dto: Filters that must always be applied.
        any_filters_dto: Filters where any can be applied.
        report_sort: Sorting parameters.
        send_full_issue_data: Whether to send full issue data.
        statuses: List of statuses to filter by.
        synchronized: Synchronization filter.

    Returns:
        Dict containing the list of deleted issues and pagination info.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter_deleted"
    params: Dict[str, Any] = {"page": page, "limit": limit, "sendFullIssueData": send_full_issue_data}
    if additional_fields:
        params["additionalFields[]"] = additional_fields
    if always_filters_dto:
        params["alwaysFiltersDTO[]"] = always_filters_dto
    if any_filters_dto:
        params["anyFiltersDTO[]"] = any_filters_dto
    if report_sort:
        params["reportSort[]"] = report_sort
    if statuses:
        params["statuses[]"] = statuses
    if synchronized:
        params["synchronized"] = synchronized

    return auth_client._request("GET", url, params=params)


def create_issue(
    auth_client: Any,
    preview_file_path: str,
    project_id: int,
    fields_json: Dict[str, Any],
    clash_test_uuid: Optional[str] = None,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new issue in a project.

    Args:
        auth_client: Authenticated pyRevizto instance.
        preview_file_path: Path to the preview file.
        project_id: The project ID.
        fields_json: Dictionary of fields for the issue.
        clash_test_uuid: Clash test UUID (optional).
        operation_id: Unique string associated with notifications (optional).

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
        FileNotFoundError: If preview file does not exist.
    """
    # API endpoint for creating an issue
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/add"

    # Generate a unique UUID for the issue
    issue_uuid = str(uuid.uuid4())

    # Read the preview file in binary mode
    # Using context manager ensures file is properly closed
    with open(preview_file_path, "rb") as file:
        # Prepare multipart: use files= for actual file and data= for fields
        files_payload = {
            "preview": (preview_file_path, file, mimetypes.guess_type(preview_file_path)[0] or "application/octet-stream"),
        }

        data_payload: Dict[str, Any] = {
            "fields": json.dumps(fields_json),
            "uuid": issue_uuid,
            "projectId": str(project_id),
        }

        if operation_id is not None:
            data_payload["operationId"] = operation_id
        if clash_test_uuid is not None:
            data_payload["clashTestUuid"] = clash_test_uuid

        return auth_client._request("POST", url, data=data_payload, files=files_payload)
