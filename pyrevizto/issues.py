import requests
import json
import uuid
import mimetypes
from typing import Optional, List, Dict, Any


def get_project_issues(
    auth_client: Any,
    project_uuid: str,
    page: int = 0,
    filters: Optional[List[Dict[str, Any]]] = None,
    sort: Optional[List[str]] = None,
    additional_fields: Optional[List[str]] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Get a list of project issues with optional filtering and sorting for a specific page.

    :param auth_client: Authenticated client instance.
    :param project_uuid: The UUID of the project.
    :param page: The page number to retrieve (default is 0).
    :param filters: A list of filters to apply to the issues.
    :param sort: A list of sorting parameters.
    :param additional_fields: A list of additional fields to include in the response.
    :param limit: The number of issues per page (default is 100).
    :return: A dictionary containing a list of issues and the total number of pages.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter"
    headers = {
        "Authorization": f"Bearer {auth_client.access_token}",
        "Content-Type": "application/json",
    }

    params = {"limit": limit, "page": page}

    if filters:
        params["alwaysFiltersDTO"] = filters

    if sort:
        params["reportSort"] = sort

    if additional_fields:
        params["additionalFields"] = additional_fields

    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=auth_client.verification_bool,
        cert=auth_client.certificate,
    )

    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()

    if data["result"] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data


def get_deleted_issues(
    auth_client: Any,
    project_uuid: str,
    page: int = 0,
    limit: int = 100,
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

    :param auth_client: Authenticated client instance.
    :param project_uuid: The UUID of the project.
    :param page: The page number to retrieve (default is 0).
    :param limit: The number of issues per page (default is 100).
    :param additional_fields: A list of additional fields to include in the response.
    :param always_filters_dto: A list of filters that must always be applied.
    :param any_filters_dto: A list of filters where any can be applied.
    :param report_sort: A list of sorting parameters.
    :param send_full_issue_data: Whether to send full issue data (default is False).
    :param statuses: A list of statuses to filter by.
    :param synchronized: A synchronization filter.

    :return:
        A dictionary containing a list of deleted issues and the total number of pages.
    """

    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter_deleted"
    headers = {
        "Authorization": f"Bearer {auth_client.access_token}",
        "Accept": "application/json",
    }
    params = {"page": page, "limit": limit, "sendFullIssueData": send_full_issue_data}
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

    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=auth_client.verification_bool,
        cert=auth_client.certificate,
    )

    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()

    if data["result"] != 0:
        raise Exception(data)

    return data


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

    :param auth_client: Authenticated client instance.
    :param preview_file_path: The path to the preview file.
    :param project_id: The project ID.
    :param fields_json: The fields for the issue in JSON format.
    :param clash_test_uuid: The clash test UUID (optional).
    :param operation_id: A unique string associated with notifications (optional).
    :return: The JSON response from the API.
    """

    # API endpoint for creating an issue
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/add"

    # Generate a unique UUID for the issue
    issue_uuid = str(uuid.uuid4())

    # Set up the headers with the bearer token
    headers = {
        "Authorization": f"Bearer {auth_client.access_token}",
        "Accept": "application/json",
    }

    # Read the preview file in binary mode
    with open(preview_file_path, "rb") as file:
        # Prepare the multipart form-data
        files = {
            "preview": (
                preview_file_path,
                file,
                mimetypes.guess_type(preview_file_path)[0],
            ),
            "fields": (None, json.dumps(fields_json), "application/json"),
            "uuid": (None, issue_uuid),
            "projectId": (None, str(project_id)),
        }

        if operation_id is not None:
            files["operationId"] = (None, operation_id)
        if clash_test_uuid is not None:
            files["clashTestUuid"] = (None, clash_test_uuid)

        # Make the POST request to the API endpoint
        response = requests.post(
            url,
            headers=headers,
            data=files,
            verify=auth_client.verification_bool,
            cert=auth_client.certificate,
        )

    # Check if the request was successful
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()

    if data["result"] != 0:
        raise Exception(data)

    return data
