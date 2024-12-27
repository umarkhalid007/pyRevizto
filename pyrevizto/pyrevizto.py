import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from .licenses import get_license_members, get_current_user_licenses, invite_users_to_license, assign_license_roles, remove_license_members
from .comments import get_issue_comments, add_comment
from .projects import get_license_projects, get_project_members, invite_users_to_project, remove_users_from_project
from .issues import get_project_issues, get_deleted_issues, create_issue
from .project_roles import get_project_roles, assign_project_role
from .users import get_current_user_info
from .stamps import get_stamp_templates
from .reports import get_user_reports
from .sheets import get_project_sheets, get_sheet_history, get_sheet_filter_options

class pyRevizto:
    def __init__(self, region, client_id=None, redirect_uri=None, state=None, scope=None, 
                 verification_bool=True, certificate=None, save_token=False, env_path='.env',
                 token_validity=timedelta(hours=0.5), refresh_token_validity=timedelta(days=30)):
        
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

    def get_tokens(self, access_code):
        if self._is_token_valid():
            return {'access_token': self.access_token, 'refresh_token': self.refresh_token}
        elif self._is_refresh_token_valid():
            return self.get_refreshed_token()
        else:
            return self._request_new_tokens(access_code)

    def get_refreshed_token(self):
        if self._is_token_valid():
            return {'access_token': self.access_token, 'refresh_token': self.refresh_token}
        elif self._is_refresh_token_valid():
            return self._request_refresh_token()
        else:
            raise ValueError("Refresh token is invalid or expired")

    def _request_new_tokens(self, access_code):
        params = {
            'grant_type': 'authorization_code',
            'code': access_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'state': self.state,
            'scope': self.scope
        }

        try:
            response = requests.post(self.token_url, data=params, verify=self.verification_bool, cert=self.certificate)
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to request new tokens: {e}")

    def _request_refresh_token(self):
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id
        }

        try:
            response = requests.post(self.token_url, data=params, verify=self.verification_bool, cert=self.certificate)
            return self._handle_token_response(response)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to refresh token: {e}")

    def _handle_token_response(self, response):
        if response.status_code == 200:
            tokens = response.json()
            if tokens.get('token_type') == 'Bearer':
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                self._save_tokens()
                return tokens
            else:
                raise PermissionError(tokens)
                
        elif response.status_code == 400:
            raise ValueError("Invalid request: Check the request parameters and try again.")
        elif response.status_code == 401:
            raise PermissionError("Unauthorized: Check your client ID and secret.")
        elif response.status_code == 403:
            raise PermissionError("Forbidden: You do not have permission to access this resource.")
        elif response.status_code == 500:
            raise RuntimeError("Server error: Try again later.")
        else:
            response.raise_for_status()

    def _update_tokens_from_file(self):
        self.access_token = os.getenv(f'{self.region}_ACCESS_TOKEN')
        self.refresh_token = os.getenv(f'{self.region}_REFRESH_TOKEN')

    def _save_tokens(self):
        if self.save_token:
            set_key(self.env_path, f'{self.region}_ACCESS_TOKEN', self.access_token)
            set_key(self.env_path, f'{self.region}_ACCESS_TOKEN_TIMESTAMP', datetime.now().isoformat())
            set_key(self.env_path, f'{self.region}_REFRESH_TOKEN', self.refresh_token)
            set_key(self.env_path, f'{self.region}_REFRESH_TOKEN_TIMESTAMP', datetime.now().isoformat())

    def _is_refresh_token_valid(self):
        refresh_token_timestamp = os.getenv(f'{self.region}_REFRESH_TOKEN_TIMESTAMP')
        if refresh_token_timestamp:
            refresh_token_timestamp = datetime.fromisoformat(refresh_token_timestamp)
            return datetime.now() <= refresh_token_timestamp + self.refresh_token_validity
        return False

    def _is_token_valid(self):
        access_token_timestamp = os.getenv(f'{self.region}_ACCESS_TOKEN_TIMESTAMP')
        if access_token_timestamp:
            access_token_timestamp = datetime.fromisoformat(access_token_timestamp)
            return datetime.now() <= access_token_timestamp + self.token_validity
        return False
    
    def _ensure_env_file_exists(self):
        if not os.path.exists(self.env_path):
            open(self.env_path, 'a').close()
            
    def _handle_error(response):
        """
        Handles errors based on the response code from the Revizto API.
    
        Parameters:
            response (dict): The JSON response from the API.
    
        Returns:
            None. Raises an exception based on the response code.
        """
        response_code = response.get('result')
        
        if response_code == 0:
            return  # Success, no error to handle
        
        
        raise Exception(response.json())
            
    def get_current_user_licenses(self,):
        return get_current_user_licenses(self)
        
    def get_license_members(self, license_id):
        return get_license_members(self, license_id)
    
    def get_issue_comments(self, project_id, issue_uuid, date, page=0):
        return get_issue_comments(self, project_id, issue_uuid, date, page=0)
    
    def get_license_projects(self, license_uuid, avatars=None, notifications=None, page=0, screenshots=None, sorting=None, type=None):
        return get_license_projects(self, license_uuid, avatars=None, notifications=None, page=0, screenshots=None, sorting=None, type=None)
    
    def get_project_issues(self, project_uuid, page=0, filters=None, sort=None, additional_fields=None, limit=100):
        return get_project_issues(self, project_uuid, page=0, filters=None, sort=None, additional_fields=None, limit=100)
    
    def add_comment(self, project_uuid, issue_uuid, comment_type, reporter, comment_text=None, file_content=None, old_watchers=None, new_watchers=None):
        return add_comment(self, project_uuid, issue_uuid, comment_type, reporter, comment_text=None, file_content=None, old_watchers=None, new_watchers=None)
    
    def invite_users_to_license(self, license_uuid, invite_data, preserve_roles=None,
                                make_guests=None, auth_method=None, deactivate=None, operation_id=None):
        return invite_users_to_license(self, license_uuid, invite_data, preserve_roles=None, 
                                           make_guests=None, auth_method=None, deactivate=None, operation_id=None)
    
    def assign_license_roles(self, license_uuid, member_uuids, role, operation_id=None):
        return assign_license_roles(self, license_uuid, member_uuids, role, operation_id=None)
    
    def remove_license_members(self, license_uuid, member_uuids, message=None, operation_id=None):
        return remove_license_members(self, license_uuid, member_uuids, message=None, operation_id=None)
    
    def get_project_members(self, project_uuid):
        return get_project_members(self, project_uuid)
    
    def invite_users_to_project(self, project_uuid, invitations, role_id, operation_id=None):
        return invite_users_to_project(self, project_uuid, invitations, role_id, operation_id=None)
    
    def get_project_roles(self, license_uuid):
        return get_project_roles(self, license_uuid)
    
    def remove_users_from_project(self, project_uuid, member_uuids, operation_id=None):
        return remove_users_from_project(self, project_uuid, member_uuids, operation_id=None)
    
    def assign_project_role(self, project_uuid, member_uuids, role_uuid, operation_id=None):
        return assign_project_role(self, project_uuid, member_uuids, role_uuid, operation_id=None)
        
    def get_current_user_info(self):
        return get_current_user_info(self)
    
    def get_stamp_templates(self, project_uuid, page=0):
        return get_stamp_templates(self, project_uuid, page=0)
    
    def get_user_reports(self, license_uuid, limit=100, page=0):
        return get_user_reports(self, license_uuid, limit=100, page=0)
    
    def get_project_sheets(self, project_uuid):
        return get_project_sheets(self, project_uuid)
    
    def get_sheet_history(self, project_uuid, sheet_uuid):
        return get_sheet_history(self, project_uuid, sheet_uuid)
    
    def get_sheet_filter_options(self, project_uuid):
        return get_sheet_filter_options(self, project_uuid)
    
    def get_deleted_issues(self, project_uuid, page=0, limit=100, additional_fields=None, 
                           always_filters_dto=None, any_filters_dto=None, report_sort=None, 
                           send_full_issue_data=False, statuses=None, synchronized=None):
        return get_deleted_issues(self, project_uuid, page=0, limit=100, additional_fields=None, 
                                  always_filters_dto=None, any_filters_dto=None, report_sort=None, 
                                  send_full_issue_data=False, statuses=None, synchronized=None)
    
    def create_issue(self, preview_file_path, project_id, fields_json, clash_test_uuid=None, operation_id=None):
        return create_issue(self, preview_file_path, project_id, fields_json, clash_test_uuid=None, operation_id=None)
    