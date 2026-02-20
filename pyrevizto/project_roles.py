from typing import Any, Dict, Optional, List

__all__ = ['get_project_roles', 'assign_project_role']

def get_project_roles(auth_client: Any, license_uuid: str) -> Dict[str, Any]:
    """
    Get the list of project roles from a license.

    Args:
        auth_client: Authenticated pyRevizto instance.
        license_uuid: UUID of the license.

    Returns:
        Dict containing the list of available project roles.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/role/list"
    return auth_client._request("GET", url)

def assign_project_role(
    auth_client: Any,
    project_uuid: str,
    member_uuids: List[str],
    role_uuid: str,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Assign a project role to one or several project members.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        member_uuids: List of UUIDs of project members.
        role_uuid: UUID of the project role to assign.
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/role/bulk-edit"
    payload: Dict[str, Any] = {'memberUuids': member_uuids, 'roleUuid': role_uuid}
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    return auth_client._request("POST", url, json=payload)
