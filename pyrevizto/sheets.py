import requests

def get_project_sheets(auth_client, project_uuid):
    """
    Get the list of project sheets.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/list"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data

def get_sheet_history(auth_client, project_uuid, sheet_uuid):
    """
    Get a sheet's version history.

    :param project_uuid: The UUID of the project.
    :param sheet_uuid: The UUID of the sheet.
    :param token: The bearer token for authorization.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/{sheet_uuid}/history"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data

def get_sheet_filter_options(auth_client, project_uuid):
    """
    Get the list of sheet filter options.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/field-variants"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data

