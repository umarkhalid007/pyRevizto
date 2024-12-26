import requests
import uuid
from datetime import datetime

def add_comment(auth_client, project_uuid, issue_uuid, comment_type, reporter, comment_text=None, file_content=None, old_watchers=None, new_watchers=None):
    """
    Adds a comment to an issue on Revizto.

    Parameters:
        auth_token (str): Bearer token for authentication.
        project_uuid (str): UUID of the project.
        issue_uuid (str): UUID of the issue.
        comment_type (str): Type of the comment (text, file, markup, diff).
        reporter (str): Email of the reporter.
        comment_text (str): Text of the comment (for text comments).
        file_content (bytes): Binary content of the file (for file and markup comments).
        old_watchers (list): List of old watchers (for diff comments).
        new_watchers (list): List of new watchers (for diff comments).

    Returns:
        dict: JSON response from the API.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/comment/add"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'multipart/form-data'
    }
    
    comment_uuid = str(uuid.uuid4())
    created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    comments = [{
        'type': comment_type,
        'uuid': comment_uuid,
        'reporter': reporter,
        'created': created_time,
        'rClashSync': False
    }]
    
    if comment_type == 'text':
        comments[0]['text'] = comment_text
    elif comment_type == 'file' or comment_type == 'markup':
        file_key = f'file_{comment_uuid}'
    elif comment_type == 'diff':
        comments[0]['diff'] = {
            'title': {
                'old': old_watchers,
                'new': new_watchers
            }
        }

    data = {
        'projectUuid': project_uuid,
        'issueUuid': issue_uuid,
        'comments': comments
    }
    
    files = None
    if file_content:
        files = {file_key: file_content}

    response = requests.post(url, headers=headers, data=data, files=files, verify=auth_client.verification_bool, cert=auth_client.certificate)
    response.raise_for_status()
    
    return response.json()


def get_issue_comments(auth_client, project_id, issue_uuid, date, page=0):
    """
    Gets issue comments added on the specified date or later.

    Parameters:
        auth_token (str): Bearer token for authentication.
        project_id (int): ID of the project.
        issue_uuid (str): UUID of the issue.
        date (str): Date in the format YYYY-MM-DD.
        page (int): Page number for pagination. Default is 0.

    Returns:
        dict: JSON response from the API.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/{issue_uuid}/comments/date"
    headers = {
        'Authorization': f'Bearer {auth_client.access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'projectId': project_id,
        'date': date,
        'page': page
    }

    response = requests.get(url, headers=headers, params=params, verify=auth_client.verification_bool, cert=auth_client.certificate)
    
    # Raise HTTPError if the request failed
    response.raise_for_status()

    return response.json()