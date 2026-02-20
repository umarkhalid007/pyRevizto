from typing import Any, Dict, Optional, List

__all__ = [
    'get_license_projects',
    'get_project_members',
    'invite_users_to_project',
    'remove_users_from_project',
]

def get_license_projects(
    auth_client: Any,
    license_uuid: str,
    avatars: Optional[bool] = None,
    notifications: Optional[bool] = None,
    page: int = 0,
    screenshots: Optional[bool] = None,
    sorting: Optional[str] = None,
    type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the current user's projects in the specified license.

    Args:
        auth_client: Authenticated pyRevizto instance.
        license_uuid: UUID of the license.
        avatars: Include avatars in the response.
        notifications: Include notifications in the response.
        page: Page number to retrieve. Defaults to 0.
        screenshots: Include screenshots in the response.
        sorting: Sorting parameter.
        type: Type parameter for filtering.

    Returns:
        Dict containing the list of projects and pagination info.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/list/{license_uuid}/paged"
    params: Dict[str, Any] = {'page': page}
    
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

    return auth_client._request("GET", url, params=params)

def get_project_members(auth_client: Any, project_uuid: str) -> Dict[str, Any]:
    """
    Get the list of project members.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.

    Returns:
        Dict containing the list of project members.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/team"
    return auth_client._request("GET", url)

def invite_users_to_project(
    auth_client: Any,
    project_uuid: str,
    invitations: List[str],
    role_id: int,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Invite users to a project.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        invitations: List of email addresses to invite.
        role_id: ID of the project role to assign to new project members.
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/invite"
    payload: Dict[str, Any] = {'invitations': invitations, 'roleId': role_id}
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    return auth_client._request("POST", url, json=payload)

def remove_users_from_project(
    auth_client: Any,
    project_uuid: str,
    member_uuids: List[str],
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Remove users from a project.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        member_uuids: List of UUIDs of project members to be removed.
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/bulk-delete"
    payload: Dict[str, Any] = {'memberUuids': member_uuids}
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    return auth_client._request("POST", url, json=payload)
