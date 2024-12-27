import requests
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any


def add_comment(
    auth_client: Any,
    project_uuid: str,
    issue_uuid: str,
    comment_type: str,
    reporter: str,
    comment_text: Optional[str] = None,
    file_content: Optional[bytes] = None,
    old_watchers: Optional[List[str]] = None,
    new_watchers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Adds a comment to an issue on Revizto.

    Parameters:
        auth_client (Any): Authenticated client instance.
        project_uuid (str): UUID of the project.
        issue_uuid (str): UUID of the issue.
        comment_type (str): Type of the comment (text, file, markup, diff).
        reporter (str): Email of the reporter.
        comment_text (Optional[str]): Text of the comment (for text comments).
        file_content (Optional[bytes]): Binary content of the file (for file and markup comments).
        old_watchers (Optional[List[str]]): List of old watchers (for diff comments).
        new_watchers (Optional[List[str]]): List of new watchers (for diff comments).

    Returns:
        Dict[str, Any]: JSON response from the API.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/comment/add"
    headers = {
        "Authorization": f"Bearer {auth_client.access_token}",
        "Content-Type": "multipart/form-data",
    }

    comment_uuid = str(uuid.uuid4())
    created_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    comments = [
        {
            "type": comment_type,
            "uuid": comment_uuid,
            "reporter": reporter,
            "created": created_timestamp,
            "rClashSync": False,
        }
    ]

    if comment_type == "text":
        comments[0]["text"] = comment_text
    elif comment_type in ["file", "markup"]:
        file_key = f"file_{comment_uuid}"
        comments[0]["file_key"] = file_key
    elif comment_type == "diff":
        comments[0]["diff"] = {"title": {"old": old_watchers, "new": new_watchers}}

    data = {
        "project_uuid": project_uuid,
        "issue_uuid": issue_uuid,
        "comments": comments,
    }

    files = {"file_content": file_content} if file_content else None

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            verify=auth_client.verification_bool,
            cert=auth_client.certificate,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to add comment: {e}")


def get_issue_comments(
    auth_client: Any, project_id: int, issue_uuid: str, date: str, page: int = 0
) -> Dict[str, Any]:
    """
    Gets issue comments added on the specified date or later.

    Parameters:
        auth_client (Any): Authenticated client instance.
        project_id (int): ID of the project.
        issue_uuid (str): UUID of the issue.
        date (str): Date in the format YYYY-MM-DD.
        page (int): Page number for pagination. Default is 0.

    Returns:
        Dict[str, Any]: JSON response from the API.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/{issue_uuid}/comments/date"
    headers = {
        "Authorization": f"Bearer {auth_client.access_token}",
        "Content-Type": "application/json",
    }

    params = {"project_id": project_id, "date": date, "page": page}

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify=auth_client.verification_bool,
            cert=auth_client.certificate,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to get issue comments: {e}")
