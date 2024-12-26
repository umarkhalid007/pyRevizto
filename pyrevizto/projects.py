import requests

def get_license_projects(auth_client, license_uuid, avatars=None, notifications=None, page=0, screenshots=None, sorting=None, type=None):
    """
    Get the current user's projects in the specified license.

    :param license_uuid: The UUID of the license.
    :param token: The bearer token for authorization.
    :param avatars: Include avatars in the response (boolean).
    :param notifications: Include notifications in the response (boolean).
    :param page: The page number to retrieve (default is 0).
    :param screenshots: Include screenshots in the response (boolean).
    :param sorting: The sorting parameter (string).
    :param type: The type parameter (string).
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/list/{license_uuid}/paged"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'page': page
    }
    
    if avatars is not None:
        params['avatars'] = avatars
    if notifications is not None:
        params['notifications'] = notifications
    if screenshots is not None:
        params['screenshots'] = screenshots
    if sorting is not None:
        params['sorting'] = sorting
    if type is not None:
        params['type'] = type

    response = requests.get(url, headers=headers, params=params, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data

def get_project_members(auth_client, project_uuid):
    """
    Get the list of project members.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/team"
    
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data

##### Giving some unkown error ####################
def invite_users_to_project(auth_client, project_uuid, invitations, role_id, operation_id=None):
    """
    Invite users to a project.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param invitations: A list of email addresses to invite.
    :param role_id: The ID of the project role to assign to new project members.
    :param operation_id: An optional unique string associated with notifications.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/invite"
    
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'invitations': invitations,
        'roleId': role_id,
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


def remove_users_from_project(auth_client, project_uuid, member_uuids, operation_id=None):
    """
    Remove users from a project.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param member_uuids: A list of UUIDs of project members to be removed.
    :param operation_id: An optional unique string associated with notifications.
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/bulk-delete"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'memberUuids': member_uuids,
        'operationId': None
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
