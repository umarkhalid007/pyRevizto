from typing import Any, Dict, Optional

__all__ = ['get_clash_groups', 'get_clashes', 'get_clash_tests']

# Default items per page for paginated endpoints
DEFAULT_PAGE_SIZE = 2000

def get_clash_groups(
    auth_client: Any,
    project_uuid: str,
    limit: int = DEFAULT_PAGE_SIZE,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Get the clash groups available in the project.

    The number of clash groups in a response is limited by the limit parameter.
    To get more clash groups, use this method multiple times with different values
    of the page parameter.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project. You can get it with Get license projects.
        limit: The number of items on a page. Must be between 2000 and 20000.
               Defaults to 2000.
        page: Page number to retrieve. Page numbering starts with 1.
              Defaults to 1. Must be between 1 and 1000000.

    Returns:
        Dict containing the clash groups and pagination info with the following structure:
        {
            'result': int,  # Response code (0 for success)
            'data': {
                'count': int,  # Total number of clash groups
                'entities': [
                    # Array of ExportedClashGroup objects
                ],
                'message': str  # Additional details about the response
            }
        }

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/clash-groups/export"
    params: Dict[str, Any] = {
        'limit': limit,
        'page': page,
    }

    return auth_client._request("GET", url, params=params)

def get_clashes(
    auth_client: Any,
    project_uuid: str,
    limit: int = DEFAULT_PAGE_SIZE,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Get the clashes available in the project.

    The number of clashes in a response is limited by the limit parameter.
    To get more clashes, use this method multiple times with different values
    of the page parameter.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project. You can get it with Get license projects.
        limit: The number of items on a page. Must be between 2000 and 20000.
               Defaults to 2000.
        page: Page number to retrieve. Page numbering starts with 1.
              Defaults to 1. Must be between 1 and 1000000.

    Returns:
        Dict containing the clashes and pagination info with the following structure:
        {
            'result': int,  # Response code (0 for success)
            'data': {
                'count': int,  # Total number of clashes
                'entities': [
                    # Array of ExportedClashItem objects
                ],
                'message': str  # Additional details about the response
            }
        }

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/clash-items/export"
    params: Dict[str, Any] = {
        'limit': limit,
        'page': page,
    }

    return auth_client._request("GET", url, params=params)

def get_clash_tests(
    auth_client: Any,
    project_uuid: str,
    limit: int = DEFAULT_PAGE_SIZE,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Get the clash tests available in the project.

    This does not include archived clash tests.

    The number of clash tests in a response is limited by the limit parameter.
    To get more clash tests, use this method multiple times with different values
    of the page parameter.

    Args:
        auth_client: Authenticated pyRevizto instance.
        project_uuid: UUID of the project. You can get it with Get license projects.
        limit: The number of items on a page. Must be between 2000 and 20000.
               Defaults to 2000.
        page: Page number to retrieve. Page numbering starts with 1.
              Defaults to 1. Must be between 1 and 1000000.

    Returns:
        Dict containing the clash tests and pagination info with the following structure:
        {
            'result': int,  # Response code (0 for success)
            'data': {
                'count': int,  # Total number of clash tests
                'entities': [
                    # Array of ExportedClashTest objects
                ],
                'message': str  # Additional details about the response
            }
        }

    Raises:
        ApiError: If the API request fails.
    """
    url = f"https://api.{auth_client.region}.revizto.com/v5/project/{project_uuid}/clash-test/export"
    params: Dict[str, Any] = {
        'limit': limit,
        'page': page,
    }

    return auth_client._request("GET", url, params=params)
