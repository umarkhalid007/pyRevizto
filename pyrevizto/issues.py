import requests
import json
import uuid
import mimetypes

def get_project_issues(auth_client, project_uuid, page=0, filters=None, sort=None, additional_fields=None, limit=100):
    """
    Get a list of project issues with optional filtering and sorting for a specific page.
    
    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param page: The page number to retrieve (default is 0).
    :param filters: A list of filters to apply to the issues.
    :param sort: A list of sorting parameters.
    :param additional_fields: A list of additional fields to include in the response.
    :param limit: The number of issues per page (default is 100).
    :return: A list of issues and the total number of pages.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'limit': limit,
        'page': page
    }

    if filters:
        params['alwaysFiltersDTO'] = filters

    if sort:
        params['reportSort'] = sort

    if additional_fields:
        params['additionalFields'] = additional_fields

    response = requests.get(url, headers=headers, params=params, verify=auth_client.verification_bool, cert = auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data

def get_deleted_issues(auth_client, project_uuid, page=0, limit=100, additional_fields=None, always_filters_dto=None, any_filters_dto=None, report_sort=None, send_full_issue_data=False, statuses=None, synchronized=None):
    """
    Get the list of issues that were deleted from a project.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param page: The page number (default is 0).
    :param limit: The number of issues on a page (default is 100).
    :param additional_fields: List of additional fields to include in the response.
    :param always_filters_dto: List of always filter DTOs.
    :param any_filters_dto: List of any filter DTOs.
    :param report_sort: List of sorting parameters.
    :param send_full_issue_data: Boolean to return all issue fields or changed fields only.
    :param statuses: List of statuses.
    :param synchronized: Date and time to retrieve only the issues that were created or updated after.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-filter/filter_deleted"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }
    params = {
        'page': page,
        'limit': limit,
        'sendFullIssueData': send_full_issue_data
    }
    if additional_fields:
        params['additionalFields[]'] = additional_fields
    if always_filters_dto:
        params['alwaysFiltersDTO[]'] = always_filters_dto
    if any_filters_dto:
        params['anyFiltersDTO[]'] = any_filters_dto
    if report_sort:
        params['reportSort[]'] = report_sort
    if statuses:
        params['statuses[]'] = statuses
    if synchronized:
        params['synchronized'] = synchronized

    response = requests.get(url, headers=headers, params=params, verify=auth_client.verification_bool, cert = auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data



def create_issue(auth_client, preview_file_path, project_id, fields_json, clash_test_uuid=None, operation_id=None):
    """
    Creates an issue in the Revizto API.

    Parameters:
    - auth_client: The authentication client with access token and region.
    - preview_file_path (str): The file path of the markup image.
    - project_id (int): The project ID.
    - fields_json (dict): The fields for the issue in JSON format.
    - clash_test_uuid (str, optional): The clash test UUID.
    - operation_id (str, optional): A unique string associated with notifications.

    Returns:
    - dict: The JSON response from the API.
    """

    # API endpoint for creating an issue
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/add"

    # Generate a unique UUID for the issue
    issue_uuid = str(uuid.uuid4())

    # Set up the headers with the bearer token
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        "Accept": "application/json",
    }

    # Read the preview file in binary mode
    with open(preview_file_path, 'rb') as file:
        # Prepare the multipart form-data
        files = {
            'preview': (preview_file_path, file, mimetypes.guess_type(preview_file_path)[0]),
            'fields': (None, json.dumps(fields_json), 'application/json'),
            'uuid': (None, issue_uuid),
            'projectId': (None, str(project_id)),
        }
        
        if operation_id is not None:
            files['operationId'] = (None, operation_id)
        if clash_test_uuid is not None:
            files['clashTestUuid'] = (None, clash_test_uuid)

        # Make the POST request to the API endpoint
        response = requests.post(url, headers=headers, data=files, verify=auth_client.verification_bool, cert = auth_client.certificate)

    # Check if the request was successful
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data
