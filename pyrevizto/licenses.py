from typing import Any, Dict, Optional, List, Union

__all__ = [
    'get_current_user_licenses',
    'get_license_members',
    'invite_users_to_license',
    'assign_license_roles',
    'remove_license_members',
]

def get_current_user_licenses(auth_client: Any) -> Dict[str, Any]:
    """
    Fetch the current user's licenses using the provided pyRevizto instance.
    
    Args:
        auth_client: Authenticated pyRevizto instance.
    
    Returns:
        Dict containing the user's license information.
    
    Raises:
        ApiError: If the API request fails.
        AuthError: If authentication fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/user/licenses"
    return auth_client._request("GET", url)
    
def get_license_members(auth_client: Any, license_id: str) -> Dict[str, Any]:
    """
    Get the list of members for a specific license.
    
    Args:
        auth_client: Authenticated pyRevizto instance.
        license_id: UUID of the license.
    
    Returns:
        Dict containing the list of license members.
    
    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_id}/team"
    return auth_client._request("GET", url)
        
def invite_users_to_license(
    auth_client: Any,
    license_uuid: str,
    invite_data: List[Dict[str, Any]],
    preserve_roles: Optional[bool] = None,
    make_guests: Optional[bool] = None,
    auth_method: Optional[str] = None,
    deactivate: Optional[bool] = None,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Invite users to a license in bulk.

    Args:
        auth_client: Authenticated pyRevizto instance.
        license_uuid: UUID of the license.
        invite_data: List of dictionaries with user information (email, role, firstName, lastName, company).
        preserve_roles: Whether to preserve current license roles for existing users.
        make_guests: Whether to grant 'Guest' role to eligible users.
        auth_method: UUID of the authentication method to set for new users.
        deactivate: Whether to deactivate the users.
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/invite/bulk"
    payload: Dict[str, Any] = {'data': invite_data}
    
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

    return auth_client._request("POST", url, json=payload)

def assign_license_roles(
    auth_client: Any,
    license_uuid: str,
    member_uuids: List[str],
    role: int,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Assign a license role to license members.

    Args:
        auth_client: Authenticated pyRevizto instance.
        license_uuid: UUID of the license.
        member_uuids: List of UUIDs of license members.
        role: License role ID (1=Guest, 2=Collaborator, 3=Content creator, 4=Administrator).
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/edit/role/bulk"
    payload: Dict[str, Any] = {'uuids': member_uuids, 'role': role}
    
    if operation_id is not None:
        payload['operationId'] = operation_id

    return auth_client._request("POST", url, json=payload)

def remove_license_members(
    auth_client: Any,
    license_uuid: str,
    member_uuids: List[str],
    message: Optional[str] = None,
    operation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Remove license members from a license.

    Args:
        auth_client: Authenticated pyRevizto instance.
        license_uuid: UUID of the license.
        member_uuids: List of UUIDs of license members to be removed.
        message: Message to send to removed users.
        operation_id: Unique string associated with notifications.

    Returns:
        Dict with the API response.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/license/{license_uuid}/remove-member/bulk"
    payload: Dict[str, Any] = {'uuids': member_uuids}
    
    if message is not None:
        payload['message'] = message
    if operation_id is not None:
        payload['operationId'] = operation_id

    return auth_client._request("POST", url, json=payload)
