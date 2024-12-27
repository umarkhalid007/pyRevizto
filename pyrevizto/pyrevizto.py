import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from typing import Optional, List, Dict, Any
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


class TokenError(Exception):
    """Custom exception for token-related errors."""

    pass


class pyRevizto:
    def __init__(
        self,
        region: str,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        scope: Optional[str] = None,
        verification_bool: bool = True,
        certificate: Optional[str] = None,
        save_token: bool = False,
        env_path: str = ".env",
        token_validity: timedelta = timedelta(hours=0.5),
        refresh_token_validity: timedelta = timedelta(days=30),
    ):
        """
        Initialize the pyRevizto instance.

        :param region: The region for the Revizto API.
        :param client_id: The client ID for OAuth2.
        :param redirect_uri: The redirect URI for OAuth2.
        :param state: The state parameter for OAuth2.
        :param scope: The scope parameter for OAuth2.
        :param verification_bool: Whether to verify SSL certificates.
        :param certificate: Path to SSL certificate.
        :param save_token: Whether to save tokens to the environment file.
        :param env_path: Path to the environment file.
        :param token_validity: Validity duration for the access token.
        :param refresh_token_validity: Validity duration for the refresh token.
        """
        self.region = region
        self.verification_bool = verification_bool
        self.certificate = certificate
        self.save_token = save_token
        self.env_path = env_path
        self.token_validity = token_validity
        self.refresh_token_validity = refresh_token_validity
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = scope
        self.token_url = f"https://api.{region}.revizto.com/v5/oauth2"
        self.access_token = None
        self.refresh_token = None
        self._ensure_env_file_exists()
        load_dotenv(env_path)
        self._update_tokens_from_file()

    def get_tokens(self, access_code: str) -> Dict[str, str]:
        if self._is_token_valid():
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            }
        elif self._is_refresh_token_valid():
            return self.get_refreshed_token()
        else:
            return self._request_new_tokens(access_code)

    def get_refreshed_token(self) -> Dict[str, str]:
        if self._is_token_valid():
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            }
        elif self._is_refresh_token_valid():
            return self._request_refresh_token()
        else:
            raise TokenError("Refresh token is invalid or expired")

    def _request_new_tokens(self, access_code: str) -> Dict[str, str]:
        params = {
            "grant_type": "authorization_code",
            "code": access_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "state": self.state,
            "scope": self.scope,
        }

        try:
            response = requests.post(
                self.token_url,
                data=params,
                verify=self.verification_bool,
                cert=self.certificate,
            )
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to request new tokens: {e}")

    def _request_refresh_token(self) -> Dict[str, str]:
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }

        try:
            response = requests.post(
                self.token_url,
                data=params,
                verify=self.verification_bool,
                cert=self.certificate,
            )
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to refresh token: {e}")

    def _handle_token_response(self, response: requests.Response) -> Dict[str, str]:
        if response.status_code == 200:
            tokens = response.json()
            if tokens.get("token_type") == "Bearer":
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
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
        self.access_token = os.getenv(f"{self.region}_ACCESS_TOKEN")
        self.refresh_token = os.getenv(f"{self.region}_REFRESH_TOKEN")

    def _save_tokens(self) -> None:
        if self.save_token:
            set_key(self.env_path, f"{self.region}_ACCESS_TOKEN", self.access_token)
            set_key(
                self.env_path,
                f"{self.region}_ACCESS_TOKEN_TIMESTAMP",
                datetime.now().isoformat(),
            )
            set_key(self.env_path, f"{self.region}_REFRESH_TOKEN", self.refresh_token)
            set_key(
                self.env_path,
                f"{self.region}_REFRESH_TOKEN_TIMESTAMP",
                datetime.now().isoformat(),
            )

    def _is_refresh_token_valid(self) -> bool:
        refresh_token_timestamp = os.getenv(f"{self.region}_REFRESH_TOKEN_TIMESTAMP")
        if refresh_token_timestamp:
            refresh_token_timestamp = datetime.fromisoformat(refresh_token_timestamp)
            return (
                datetime.now() <= refresh_token_timestamp + self.refresh_token_validity
            )
        return False

    def _is_token_valid(self) -> bool:
        access_token_timestamp = os.getenv(f"{self.region}_ACCESS_TOKEN_TIMESTAMP")
        if access_token_timestamp:
            access_token_timestamp = datetime.fromisoformat(access_token_timestamp)
            return datetime.now() <= access_token_timestamp + self.token_validity
        return False

    def _ensure_env_file_exists(self) -> None:
        if not os.path.exists(self.env_path):
            open(self.env_path, "a").close()

    def _handle_error(response: requests.Response) -> None:
        """
        Handles errors based on the response code from the Revizto API.

        Parameters:
            response (requests.Response): The response from the API.

        Returns:
            None. Raises an exception based on the response code.
        """
        response_code = response.json().get("result")

        if response_code == 0:
            return  # Success, no error to handle

        raise Exception(response.json())

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
        filters: Optional[List[Dict[str, Any]]] = None,
        sort: Optional[List[str]] = None,
        additional_fields: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Any:
        return get_project_issues(
            self, project_uuid, page, filters, sort, additional_fields, limit
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
