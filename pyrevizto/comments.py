import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

__all__ = ['add_comment', 'get_issue_comments']

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
    Add a comment to an issue on Revizto.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        issue_uuid: UUID of the issue.
        comment_type: Type of comment (text, file, markup, diff).
        reporter: Email of the reporter.
        comment_text: Text of the comment (for text comments).
        file_content: Binary content of the file (for file and markup comments).
        old_watchers: List of old watchers (for diff comments).
        new_watchers: List of new watchers (for diff comments).

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/comment/add"

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

    data: Dict[str, Any] = {
        "project_uuid": project_uuid,
        "issue_uuid": issue_uuid,
        "comments": comments,
    }

    files_payload = None
    if file_content:
        # requests will set the correct multipart boundary when using files=
        files_payload = {f"file_{comment_uuid}": (f"file_{comment_uuid}", file_content)}

    # Use client's centralized request helper which handles auth/refresh/errors
    # comments must be sent as JSON string in the 'comments' field
    payload_data = {k: (json.dumps(v) if k == 'comments' else v) for k, v in data.items()}
    return auth_client._request("POST", url, data=payload_data, files=files_payload)

def get_issue_comments(
    auth_client: Any,
    project_id: int,
    issue_uuid: str,
    date: str,
    page: int = 0,
) -> Dict[str, Any]:
    """
    Get issue comments added on the specified date or later.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_id: ID of the project.
        issue_uuid: UUID of the issue.
        date: Date in format YYYY-MM-DD.
        page: Page number for pagination. Defaults to 0.

    Returns:
        Dict containing the list of comments.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/issue/{issue_uuid}/comments/date"
    params: Dict[str, Any] = {"project_id": project_id, "date": date, "page": page}
    return auth_client._request("GET", url, params=params)
