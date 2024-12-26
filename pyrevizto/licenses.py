import requests

def get_current_user_licenses(auth_client):
    """Fetch the current user's licenses using the provided pyRevizto instance."""
    if not auth_client.access_token:
        raise ValueError("Access token is not available.")

    url = f"https://api.{auth_client.region}.revizto.com/v5/user/licenses"
    
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)

    if response.status_code == 401:  # Token expired
        auth_client.refresh_tokens()
        headers['Authorization'] = f"Bearer {auth_client.access_token}"
        response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.text
    
def get_license_members(auth_client, license_id):
    if not auth_client.access_token:
        raise ValueError("Access token is not available.")

    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_id}/team"

    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers, verify=auth_client.verification_bool, cert=auth_client.certificate)

    if response.status_code == 200:
        if response.json().get("result") == -206:  # Token expired
            auth_client.get_refreshed_token()
            headers['Authorization'] = f"Bearer {auth_client.access_token}"
            response = requests.get(url, headers=headers)

        return response.json()
    else:
        return response.text
        
def invite_users_to_license(auth_client, license_uuid, invite_data, preserve_roles=None, 
                            make_guests=None, auth_method=None, deactivate=None, operation_id=None):
    """
    Invite users to a license.

    :param license_uuid: The UUID of the license.
    :param token: The bearer token for authorization.
    :param invite_data: A list of dictionaries, where each dictionary contains user information.
    :param preserve_roles: Whether to preserve current license roles for existing users (boolean).
    :param make_guests: Whether to grant 'Guest' role to eligible users (boolean).
    :param auth_method: The UUID of the authentication method to set for new users (string).
    :param deactivate: Whether to deactivate the users (boolean).
    :param operation_id: A unique string associated with notifications (string).
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/invite/bulk"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }
    #invite_data should be an array
    payload = {
        'data': invite_data
    }
    
    if preserve_roles is not None:
        payload['preserveRoles'] = preserve_roles
    if make_guests is not None:
        payload['makeGuests'] = make_guests
    if auth_method is not None:
        payload['authMethod'] = auth_method
    if deactivate is not None:
        payload['deactivate'] = deactivate
    if operation_id is not None:
        payload['operationId'] = operation_id

    response = requests.post(url, headers=headers, json=payload, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data

def assign_license_roles(auth_client, license_uuid, member_uuids, role, operation_id=None):
    """
    Assign a license role to license members.

    :param license_uuid: The UUID of the license.
    :param token: The bearer token for authorization.
    :param member_uuids: A list of UUIDs of license members.
    :param role: The license role to assign (integer: 1-Guest, 2-Collaborator, 3-Content creator, 4-License administrator).
    :param operation_id: A unique string associated with notifications (optional).
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/edit/role/bulk"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'uuids': member_uuids,
        'role': role,
    }
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    response = requests.post(url, headers=headers, json=payload, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data

def remove_license_members(auth_client, license_uuid, member_uuids, message=None, operation_id=None):
    """
    Remove license members from a license.

    :param license_uuid: The UUID of the license.
    :param token: The bearer token for authorization.
    :param member_uuids: A list of UUIDs of license members to be removed.
    :param message: The message to be sent to the users removed from the license (optional).
    :param operation_id: A unique string associated with notifications (optional).
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/remove-member/bulk"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'uuids': member_uuids
    }
    
    if message is not None:
        payload['message'] = message
    if operation_id is not None:
        payload['operationId'] = operation_id

    response = requests.post(url, headers=headers, json=payload, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(f"API Error: {data['message']}")

    return data
