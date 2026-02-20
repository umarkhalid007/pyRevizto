from typing import Any, Dict

__all__ = ['get_current_user_info']

def get_current_user_info(auth_client: Any) -> Dict[str, Any]:
    """
    Get the details of the current user.

    Args:
        auth_client: Authenticated pyRevizto instance.

    Returns:
        Dict containing the current user's information.

    Raises:
        ApiError: If the API request fails.
        AuthError: If authentication fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/user"
    return auth_client._request("GET", url)