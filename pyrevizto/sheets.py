from typing import Any, Dict

__all__ = ['get_project_sheets', 'get_sheet_history', 'get_sheet_filter_options']

def get_project_sheets(auth_client: Any, project_uuid: str) -> Dict[str, Any]:
    """
    Get the list of project sheets.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.

    Returns:
        Dict containing the list of project sheets.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/list"
    return auth_client._request("GET", url)

def get_sheet_history(auth_client: Any, project_uuid: str, sheet_uuid: str) -> Dict[str, Any]:
    """
    Get a sheet's version history.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.
        sheet_uuid: UUID of the sheet.

    Returns:
        Dict containing the sheet version history.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/{sheet_uuid}/history"
    return auth_client._request("GET", url)

def get_sheet_filter_options(auth_client: Any, project_uuid: str) -> Dict[str, Any]:
    """
    Get the list of sheet filter options.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project.

    Returns:
        Dict containing the available sheet filter options.

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/sheet/field-variants"
    return auth_client._request("GET", url)

