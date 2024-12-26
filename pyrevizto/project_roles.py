import requests

def get_project_roles(auth_client, license_uuid):
    """
    Get the list of project roles from a license.

    :param license_uuid: The UUID of the license.
    :param token: The bearer token for authorization.
    :return: A JSON object with the response data.
    """
    
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/role/list"
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

def assign_project_role(auth_client, project_uuid, member_uuids, role_uuid, operation_id=None):
    """
    Assign a project role to one or several project members.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param member_uuids: A list of UUIDs of project members.
    :param role_uuid: The UUID of the project role to assign.
    :param operation_id: An optional unique string associated with notifications.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/bulk-edit"
    
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'memberUuids': member_uuids,
        'roleUuid': role_uuid
    }
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    response = requests.post(url, headers=headers, json=payload, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data
