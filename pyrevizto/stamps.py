import requests

def get_stamp_templates(auth_client, project_uuid, page=0):
    """
    Get the stamp templates and stamp template categories available in the project.

    :param project_uuid: The UUID of the project.
    :param token: The bearer token for authorization.
    :param page: The page number (default is 0).
    :return: A JSON object with the response data.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-preset/list"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Accept': 'application/json'
    }
    params = {
        'page': page
    }

    response = requests.get(url, headers=headers, params=params, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    
    if data['result'] != 0:
        raise Exception(data)

    return data