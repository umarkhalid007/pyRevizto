import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv, set_key
from typing import Optional, Union, List, Dict, Any
import logging

# Module-level logger for debugging and monitoring
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Basic configuration only if the application hasn't configured logging
    logging.basicConfig(level=logging.INFO)
from .licenses import (
    get_license_members,
    get_current_user_licenses,
    invite_users_to_license,
    assign_license_roles,
    remove_license_members,
)
from .comments import get_issue_comments, add_comment
from .projects import (
    get_license_projects,
    get_project_members,
    invite_users_to_project,
    remove_users_from_project,
)
from .issues import get_project_issues, get_deleted_issues, create_issue
from .project_roles import get_project_roles, assign_project_role
from .users import get_current_user_info
from .stamps import get_stamp_templates
from .reports import get_user_reports
from .sheets import get_project_sheets, get_sheet_history, get_sheet_filter_options
from .clashes import get_clash_groups, get_clashes, get_clash_tests


class TokenError(Exception):
    """Raised when token-related operations fail."""
    pass


class ApiError(Exception):
    """Raised when API returns an error payload or non-OK status.
    
    Attributes:
        status_code: HTTP status code from the failed request
        payload: Response body from the API (dict or str)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        payload: Optional[Union[dict, str]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class AuthError(ApiError):
    """Raised for authentication-related errors (401, invalid tokens, etc)."""
    pass


class pyRevizto:
    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        region: str,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        scope: Optional[str] = None,
        verification_bool: Union[bool, str] = True,
        certificate: Optional[str] = None,
        save_token: bool = False,
        env_path: str = ".env",
        token_validity: timedelta = timedelta(hours=0.5),
        refresh_token_validity: timedelta = timedelta(days=30),
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the pyRevizto instance.

        Args:
            region: The region for the Revizto API (e.g., 'eu', 'us').
            client_id: The client ID for OAuth2.
            redirect_uri: The redirect URI for OAuth2.
            state: The state parameter for OAuth2.
            scope: The scope parameter for OAuth2.
            verification_bool: Whether to verify SSL certificates (True/False or path to CA bundle).
            certificate: Path to client SSL certificate for mTLS.
            save_token: Whether to save tokens to the environment file.
            env_path: Path to the .env file for token storage.
            token_validity: Validity duration for the access token.
            refresh_token_validity: Validity duration for the refresh token.
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self.region = region
        self.verification_bool = verification_bool
        self.certificate = certificate
        self.save_token = save_token
        self.env_path = env_path
        self.token_validity = token_validity
        self.refresh_token_validity = refresh_token_validity
        self.timeout = timeout
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = scope
        self.token_url = f"https://api.{region}.revizto.com/v5/oauth2"
        self.access_token = None
        self.refresh_token = None
        self.token_expiration: Optional[datetime] = None
        self.refresh_token_expiration: Optional[datetime] = None
        # Use a requests.Session for connection reuse and easier testing
        self.session = requests.Session()
        if self.save_token:
            self._ensure_env_file_exists()
            load_dotenv(env_path)
            self._update_tokens_from_file()

    def get_tokens(self, access_code: str) -> Optional[Dict[str, Any]]:
        if self._is_token_valid():
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            }
        elif self._is_refresh_token_valid():
            return self.get_refreshed_token()
        else:
            return self._request_new_tokens(access_code)

    def get_refreshed_token(self) -> Optional[Dict[str, Any]]:
        if self._is_token_valid():
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            }
        elif self._is_refresh_token_valid():
            return self._request_refresh_token()
        else:
            raise TokenError("Refresh token is invalid or expired")

    def _request_new_tokens(self, access_code: str) -> Optional[Dict[str, Any]]:
        params = {
            "grant_type": "authorization_code",
            "code": access_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "state": self.state,
            "scope": self.scope,
        }

        try:
            response = self.session.post(
                self.token_url,
                data=params,
                verify=self.verification_bool,
                cert=self.certificate,
            )
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to request new tokens: {e}")

    def _request_refresh_token(self) -> Optional[Dict[str, Any]]:
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }

        try:
            response = self.session.post(
                self.token_url,
                data=params,
                verify=self.verification_bool,
                cert=self.certificate,
            )
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to refresh token: {e}")

    def _handle_token_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        if response.status_code == 200:
            tokens = response.json()
            if tokens.get("token_type") == "Bearer" or tokens.get("access_token"):
                # Set tokens
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")

                now = datetime.now(timezone.utc)
                # access token expiry: prefer expires_in from response
                expires_in = tokens.get("expires_in")
                if expires_in is not None:
                    try:
                        self.token_expiration = now + timedelta(seconds=int(expires_in))
                    except Exception:
                        self.token_expiration = now + self.token_validity
                else:
                    # fallback to configured default validity
                    self.token_expiration = now + self.token_validity

                # refresh token expiry: prefer refresh_expires_in if available
                refresh_expires_in = tokens.get("refresh_expires_in")
                if refresh_expires_in is not None:
                    try:
                        self.refresh_token_expiration = now + timedelta(seconds=int(refresh_expires_in))
                    except Exception:
                        self.refresh_token_expiration = now + self.refresh_token_validity
                else:
                    self.refresh_token_expiration = now + self.refresh_token_validity

                # persist if requested
                self._save_tokens()
                return tokens
            else:
                raise PermissionError(tokens)
        elif response.status_code == 400:
            raise ValueError(
                "Invalid request: Check the request parameters and try again."
            )
        elif response.status_code == 401:
            raise PermissionError("Unauthorized: Check your client ID and secret.")
        elif response.status_code == 403:
            raise PermissionError(
                "Forbidden: You do not have permission to access this resource."
            )
        elif response.status_code == 500:
            raise RuntimeError("Server error: Try again later.")
        else:
            response.raise_for_status()

    def _update_tokens_from_file(self) -> None:
        """Load tokens from environment file if they exist."""
        if os.getenv(f"{self.region}_ACCESS_TOKEN_TIMESTAMP"):
            try:
                self.access_token = os.getenv(f"{self.region}_ACCESS_TOKEN")
                self.refresh_token = os.getenv(f"{self.region}_REFRESH_TOKEN")
                ts_str = os.getenv(f"{self.region}_ACCESS_TOKEN_TIMESTAMP")
                rt_str = os.getenv(f"{self.region}_REFRESH_TOKEN_TIMESTAMP")
                if ts_str:
                    self.token_expiration = datetime.fromisoformat(ts_str)
                if rt_str:
                    self.refresh_token_expiration = datetime.fromisoformat(rt_str)
                logger.debug(f"Loaded tokens from {self.env_path} for region {self.region}")
            except Exception as e:
                # If parsing fails, clear the values so they get refreshed
                logger.warning(
                    f"Failed to parse stored tokens from {self.env_path}: {e}. "
                    "Tokens will be re-fetched."
                )
                self.access_token = None
                self.refresh_token = None
                self.token_expiration = None
                self.refresh_token_expiration = None

    def _save_tokens(self) -> None:
        """Save tokens to environment file for persistence."""
        if self.save_token:
            try:
                set_key(self.env_path, f"{self.region}_ACCESS_TOKEN", self.access_token or "")
                set_key(
                    self.env_path,
                    f"{self.region}_ACCESS_TOKEN_TIMESTAMP",
                    self.token_expiration.isoformat() if self.token_expiration else "",
                )
                set_key(self.env_path, f"{self.region}_REFRESH_TOKEN", self.refresh_token or "")
                set_key(
                    self.env_path,
                    f"{self.region}_REFRESH_TOKEN_TIMESTAMP",
                    self.refresh_token_expiration.isoformat() if self.refresh_token_expiration else "",
                )
                logger.debug(f"Tokens saved to {self.env_path}")
            except Exception as e:
                logger.error(f"Failed to save tokens to {self.env_path}: {e}")

    def _is_refresh_token_valid(self) -> bool:
        if self.refresh_token_expiration:
            return datetime.now(timezone.utc) < self.refresh_token_expiration
        return False

    def _is_token_valid(self) -> bool:
        if self.token_expiration:
            return datetime.now(timezone.utc) < self.token_expiration
        return False

    def _ensure_env_file_exists(self) -> None:
        if not os.path.exists(self.env_path):
            open(self.env_path, "a").close()

    def refresh_tokens(self) -> Optional[Dict[str, Any]]:
        """Public helper to refresh tokens; kept for backward compatibility."""
        return self.get_refreshed_token()

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_on_401: bool = True,
        timeout: Optional[float] = None,
    ) -> Any:
        """Central request helper.

        Centralizes all HTTP request handling including:
        - Automatic Authorization header attachment
        - Automatic token refresh on 401 (once)
        - JSON parsing and error handling
        - Timeout configuration
        - Structured exception raising

        Args:
            method: HTTP method (GET, POST, etc.)
            url: The request URL
            params: Query parameters
            json: JSON body
            data: Form data
            files: Files for multipart upload
            headers: Additional headers
            retry_on_401: Whether to retry after token refresh on 401
            timeout: Request timeout in seconds. Uses instance default if None.

        Returns:
            Parsed JSON response or text

        Raises:
            ApiError: For HTTP errors or API errors
            AuthError: For authentication failures
        """
        session = getattr(self, "session", requests)
        timeout = timeout or self.timeout

        headers = headers.copy() if headers else {}
        if self.access_token:
            headers.setdefault("Authorization", f"Bearer {self.access_token}")

        try:
            resp = session.request(
                method, url, params=params, json=json, data=data, files=files,
                headers=headers, verify=self.verification_bool, cert=self.certificate,
                timeout=timeout
            )
        except requests.RequestException as e:
            raise ApiError(f"Network error: {e}")

        if resp.status_code == 401 and retry_on_401:
            # Try refresh then retry once
            try:
                self.get_refreshed_token()
            except TokenError:
                raise AuthError("Authentication failed and refresh token is invalid", status_code=401)

            # update header and retry
            headers["Authorization"] = f"Bearer {self.access_token}"
            try:
                resp = session.request(
                    method, url, params=params, json=json, data=data, files=files,
                    headers=headers, verify=self.verification_bool, cert=self.certificate,
                    timeout=timeout
                )
            except requests.RequestException as e:
                raise ApiError(f"Network error after refresh: {e}")

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # include response body if available
            content = None
            try:
                content = resp.json()
            except Exception:
                content = resp.text
            raise ApiError(f"HTTP {resp.status_code}: {resp.reason}", status_code=resp.status_code, payload=content)

        # parse JSON if possible
        try:
            parsed = resp.json()
        except Exception:
            return resp.text

        # If API uses result code, treat non-zero as error
        if isinstance(parsed, dict) and parsed.get("result") is not None and parsed.get("result") != 0:
            raise ApiError(parsed.get("message", "API returned an error"), status_code=resp.status_code, payload=parsed)

        return parsed


    def get_current_user_licenses(self) -> Any:
        return get_current_user_licenses(self)

    def get_license_members(self, license_id: str) -> Any:
        return get_license_members(self, license_id)

    def get_issue_comments(
        self, project_id: int, issue_uuid: str, date: str, page: int = 0
    ) -> Any:
        return get_issue_comments(self, project_id, issue_uuid, date, page)

    def get_license_projects(
        self,
        license_uuid: str,
        avatars: Optional[bool] = None,
        notifications: Optional[bool] = None,
        page: int = 0,
        screenshots: Optional[bool] = None,
        sorting: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Any:
        return get_license_projects(
            self, license_uuid, avatars, notifications, page, screenshots, sorting, type
        )

    def get_project_issues(
        self,
        project_uuid: str,
        page: int = 0,
        always_filters: Optional[List[Dict[str, Any]]] = None,
        any_filters: Optional[List[Dict[str, Any]]] = None,
        additional_fields: Optional[List[str]] = None,
        report_sort: Optional[List[Dict[str, str]]] = None,
        limit: int = 100,
        send_full_issue_data: bool = False,
        synchronized: Optional[str] = None,
    ) -> Any:
        return get_project_issues(
            self, project_uuid, page, always_filters, any_filters, additional_fields, report_sort, limit, send_full_issue_data, synchronized
        )

    def add_comment(
        self,
        project_uuid: str,
        issue_uuid: str,
        comment_type: str,
        reporter: str,
        comment_text: Optional[str] = None,
        file_content: Optional[bytes] = None,
        old_watchers: Optional[List[str]] = None,
        new_watchers: Optional[List[str]] = None,
    ) -> Any:
        return add_comment(
            self,
            project_uuid,
            issue_uuid,
            comment_type,
            reporter,
            comment_text,
            file_content,
            old_watchers,
            new_watchers,
        )

    def invite_users_to_license(
        self,
        license_uuid: str,
        invite_data: List[Dict[str, Any]],
        preserve_roles: Optional[bool] = None,
        make_guests: Optional[bool] = None,
        auth_method: Optional[str] = None,
        deactivate: Optional[bool] = None,
        operation_id: Optional[str] = None,
    ) -> Any:
        return invite_users_to_license(
            self,
            license_uuid,
            invite_data,
            preserve_roles,
            make_guests,
            auth_method,
            deactivate,
            operation_id,
        )

    def assign_license_roles(
        self,
        license_uuid: str,
        member_uuids: List[str],
        role: int,
        operation_id: Optional[str] = None,
    ) -> Any:
        return assign_license_roles(
            self, license_uuid, member_uuids, role, operation_id
        )

    def remove_license_members(
        self,
        license_uuid: str,
        member_uuids: List[str],
        message: Optional[str] = None,
        operation_id: Optional[str] = None,
    ) -> Any:
        return remove_license_members(
            self, license_uuid, member_uuids, message, operation_id
        )

    def get_project_members(self, project_uuid: str) -> Any:
        return get_project_members(self, project_uuid)

    def invite_users_to_project(
        self,
        project_uuid: str,
        invitations: List[str],
        role_id: int,
        operation_id: Optional[str] = None,
    ) -> Any:
        return invite_users_to_project(
            self, project_uuid, invitations, role_id, operation_id
        )

    def get_project_roles(self, license_uuid: str) -> Any:
        return get_project_roles(self, license_uuid)

    def remove_users_from_project(
        self,
        project_uuid: str,
        member_uuids: List[str],
        operation_id: Optional[str] = None,
    ) -> Any:
        return remove_users_from_project(self, project_uuid, member_uuids, operation_id)

    def assign_project_role(
        self,
        project_uuid: str,
        member_uuids: List[str],
        role_uuid: str,
        operation_id: Optional[str] = None,
    ) -> Any:
        return assign_project_role(
            self, project_uuid, member_uuids, role_uuid, operation_id
        )

    def get_current_user_info(self) -> Any:
        return get_current_user_info(self)

    def get_stamp_templates(self, project_uuid: str, page: int = 0) -> Any:
        return get_stamp_templates(self, project_uuid, page)

    def get_user_reports(
        self, license_uuid: str, limit: int = 100, page: int = 0
    ) -> Any:
        return get_user_reports(self, license_uuid, limit, page)

    def get_project_sheets(self, project_uuid: str) -> Any:
        return get_project_sheets(self, project_uuid)

    def get_sheet_history(self, project_uuid: str, sheet_uuid: str) -> Any:
        return get_sheet_history(self, project_uuid, sheet_uuid)

    def get_sheet_filter_options(self, project_uuid: str) -> Any:
        return get_sheet_filter_options(self, project_uuid)

    def get_deleted_issues(
        self,
        project_uuid: str,
        page: int = 0,
        limit: int = 100,
        additional_fields: Optional[List[str]] = None,
        always_filters_dto: Optional[List[Dict[str, Any]]] = None,
        any_filters_dto: Optional[List[Dict[str, Any]]] = None,
        report_sort: Optional[List[str]] = None,
        send_full_issue_data: bool = False,
        statuses: Optional[List[str]] = None,
        synchronized: Optional[str] = None,
    ) -> Any:
        return get_deleted_issues(
            self,
            project_uuid,
            page,
            limit,
            additional_fields,
            always_filters_dto,
            any_filters_dto,
            report_sort,
            send_full_issue_data,
            statuses,
            synchronized,
        )

    def create_issue(
        self,
        preview_file_path: str,
        project_id: int,
        fields_json: Dict[str, Any],
        clash_test_uuid: Optional[str] = None,
        operation_id: Optional[str] = None,
    ) -> Any:
        return create_issue(
            self,
            preview_file_path,
            project_id,
            fields_json,
            clash_test_uuid,
            operation_id,
        )

    def get_clash_groups(
        self,
        project_uuid: str,
        limit: int = 2000,
        page: int = 1,
    ) -> Any:
        return get_clash_groups(self, project_uuid, limit, page)

    def get_clashes(
        self,
        project_uuid: str,
        limit: int = 2000,
        page: int = 1,
    ) -> Any:
        return get_clashes(self, project_uuid, limit, page)

    def get_clash_tests(
        self,
        project_uuid: str,
        limit: int = 2000,
        page: int = 1,
    ) -> Any:
        return get_clash_tests(self, project_uuid, limit, page)