from typing import Any, Dict

__all__ = ['get_stamp_templates']

def get_stamp_templates(
    auth_client: Any,
    project_uuid: str,
    page: int = 0,
) -> Dict[str, Any]:
    """
    Get the stamp templates and stamp template categories available in the project.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        page: Page number for pagination. Defaults to 0.

    Returns:
        Dict containing the stamp templates and categories.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/issue-preset/list"
    params = {'page': page}
    return auth_client._request("GET", url, params=params)