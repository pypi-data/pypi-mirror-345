import json
import requests
from typing import Dict, Optional, Any, Union, List
from .base_client import BaseClient

class UserClient(BaseClient):
    """
    Client for interacting with Storylinez User API.
    Provides methods for accessing user profiles, storage information, and subscription details.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the UserClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.user_url = f"{self.base_url}/user"
    
    # User Profile Methods
    
    def get_current_user(self) -> Dict:
        """
        Get information about the currently authenticated user.
        
        Returns:
            Dictionary with current user profile information including:
            - id: User ID
            - username: Username
            - first_name: First name
            - last_name: Last name
            - image_url: Profile image URL
            - email_addresses: List of email addresses associated with the account
            - phone_numbers: List of phone numbers associated with the account
            - public_metadata: Public metadata associated with the user
            - created_at: Account creation timestamp
            - updated_at: Last update timestamp
            - last_sign_in_at: Last sign-in timestamp
            - profile_image_url: Profile image URL
        
        Raises:
            requests.RequestException: If the API call fails
            ValueError: If the response cannot be parsed
        """
        try:
            response = self._make_request("GET", f"{self.user_url}/me")
            if 'data' in response:
                return response['data']
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, "Failed to retrieve current user profile")
    
    def get_user(self, user_id: str) -> Dict:
        """
        Get information about a specific user.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            Dictionary with public user profile information including:
            - id: User ID
            - username: Username (if set)
            - first_name: First name
            - last_name: Last name
            - image_url: Profile image URL
            - public_metadata: Public metadata
            
        Raises:
            ValueError: If user_id is empty or doesn't start with 'user_'
            requests.RequestException: If the API call fails
        """
        # Validate user_id format
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not user_id.startswith('user_'):
            raise ValueError("User ID must start with 'user_'")
        
        try:
            response = self._make_request("GET", f"{self.user_url}/user/{user_id}")
            if 'data' in response:
                return response['data']
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve user profile for {user_id}")
    
    # Storage Methods
    
    def get_user_storage(self, org_id: str = None) -> Dict:
        """
        Get storage usage information for a user within an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with storage used by the user within the specified organization:
            - storage_used: Storage used in bytes
            - user_id: ID of the user
            - org_id: ID of the organization
            
        Raises:
            ValueError: If org_id is not provided and no default is set
            requests.RequestException: If the API call fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate org_id format
        if not org_id.startswith('org_'):
            raise ValueError("Organization ID must start with 'org_'")
            
        params = {"org_id": org_id}
        
        try:
            response = self._make_request("GET", f"{self.user_url}/storage", params=params)
            
            # Add some helpful data conversion for display
            if 'storage_used' in response:
                # Add conversion to MB and GB for convenience
                storage_bytes = response['storage_used']
                response['storage_used_mb'] = storage_bytes / (1024 * 1024)
                response['storage_used_gb'] = storage_bytes / (1024 * 1024 * 1024)
                response['storage_used_formatted'] = self._format_bytes(storage_bytes)
            
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve storage usage for organization {org_id}")
    
    def get_org_storage(self, org_id: str = None, include_breakdown: bool = False) -> Dict:
        """
        Get storage usage information for an entire organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            include_breakdown: If True, includes a user-by-user breakdown of storage usage
            
        Returns:
            Dictionary with total storage used by the organization and optional user breakdown:
            - org_id: ID of the organization
            - total_storage_used: Total storage used in bytes
            - user_count: Number of users in the organization
            - breakdown: (optional) List of user storage entries if include_breakdown is True
            
        Raises:
            ValueError: If org_id is not provided and no default is set
            requests.RequestException: If the API call fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate org_id format
        if not org_id.startswith('org_'):
            raise ValueError("Organization ID must start with 'org_'")
            
        # Ensure boolean parameter is properly formatted
        include_breakdown_str = str(include_breakdown).lower()
        if include_breakdown_str not in ('true', 'false'):
            raise ValueError("include_breakdown must be a boolean value")
            
        params = {
            "org_id": org_id,
            "include_breakdown": include_breakdown_str
        }
        
        try:
            response = self._make_request("GET", f"{self.user_url}/org/storage", params=params)
            
            # Add some helpful data conversion for display
            if 'total_storage_used' in response:
                # Add conversion to MB and GB for convenience
                storage_bytes = response['total_storage_used']
                response['total_storage_used_mb'] = storage_bytes / (1024 * 1024)
                response['total_storage_used_gb'] = storage_bytes / (1024 * 1024 * 1024)
                response['total_storage_used_formatted'] = self._format_bytes(storage_bytes)
            
            # Add formatted storage to breakdown items if present
            if include_breakdown and 'breakdown' in response and response['breakdown']:
                for user_entry in response['breakdown']:
                    if 'storage_used' in user_entry:
                        user_entry['storage_used_formatted'] = self._format_bytes(user_entry['storage_used'])
            
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve organization storage for {org_id}")
    
    # Subscription Methods
    
    def get_subscription(self, org_id: str = None) -> Dict:
        """
        Get detailed subscription information for an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with subscription details including:
            - subscription_id: ID of the subscription
            - tier: Subscription tier level (numeric)
            - plan_name: Name of the subscription plan
            - period: Information about the current billing period
            - projects: Project limits and usage information
            - storage: Storage limits and usage information
            - content_processing: Content processing limits and usage information
            - reset_schedules: When various limits reset
            
        Raises:
            ValueError: If org_id is not provided and no default is set
            requests.RequestException: If the API call fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate org_id format
        if not org_id.startswith('org_'):
            raise ValueError("Organization ID must start with 'org_'")
            
        params = {"org_id": org_id}
        
        try:
            return self._make_request("GET", f"{self.user_url}/subscription", params=params)
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve subscription information for organization {org_id}")
    
    def get_project_usage(self, org_id: str = None) -> Dict:
        """
        Get project usage information and limits.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with project usage information including:
            - monthly_limit: Monthly project limit
            - monthly_used: Projects used in current billing period
            - monthly_remaining: Projects remaining in current billing period
            - daily_limit: Daily project limit
            - daily_used: Projects used today
            - daily_remaining: Projects remaining today
            - tier: Subscription tier level
            - plan_name: Name of the subscription plan
            - period_start: Beginning of current billing period
            - period_end: End of current billing period
            - reset_schedules: When various limits reset
            
        Raises:
            ValueError: If org_id is not provided and no default is set
            requests.RequestException: If the API call fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate org_id format
        if not org_id.startswith('org_'):
            raise ValueError("Organization ID must start with 'org_'")
            
        params = {"org_id": org_id}
        
        try:
            response = self._make_request("GET", f"{self.user_url}/projects/usage", params=params)
            
            # Add some helpful properties
            if 'daily_limit' in response and 'daily_used' in response:
                # Add percentage calculation for visualization
                daily_limit = response.get('daily_limit', 0)
                daily_used = response.get('daily_used', 0)
                if daily_limit > 0:
                    response['daily_usage_percentage'] = min(100, round((daily_used / daily_limit) * 100, 1))
                else:
                    response['daily_usage_percentage'] = 0
            
            if 'monthly_limit' in response and 'monthly_used' in response:
                # Add percentage calculation for visualization
                monthly_limit = response.get('monthly_limit', 0)
                monthly_used = response.get('monthly_used', 0)
                if monthly_limit > 0:
                    response['monthly_usage_percentage'] = min(100, round((monthly_used / monthly_limit) * 100, 1))
                else:
                    response['monthly_usage_percentage'] = 0
            
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve project usage for organization {org_id}")
    
    def get_extra_projects(self, org_id: str = None) -> Dict:
        """
        Get extra projects information and costs.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with extra projects information including:
            - extra_projects: Number of extra projects used
            - extra_projects_cost: Cost of extra projects
            - monthly_limit: Monthly project limit
            - monthly_used: Projects used in current billing period
            - can_create_extra_projects: Whether the organization can create extra projects
            - billing_period: Current billing period start and end dates
            
        Raises:
            ValueError: If org_id is not provided and no default is set
            requests.RequestException: If the API call fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate org_id format
        if not org_id.startswith('org_'):
            raise ValueError("Organization ID must start with 'org_'")
            
        params = {"org_id": org_id}
        
        try:
            response = self._make_request("GET", f"{self.user_url}/projects/extras", params=params)
            
            # Add convenience fields for display
            if 'extra_projects' in response and 'monthly_limit' in response:
                # Calculate the total overage percentage
                monthly_limit = response.get('monthly_limit', 0)
                extra_projects = response.get('extra_projects', 0)
                if monthly_limit > 0:
                    response['overage_percentage'] = round((extra_projects / monthly_limit) * 100, 1)
                else:
                    response['overage_percentage'] = 0
            
            return response
        except requests.RequestException as e:
            self._handle_request_error(e, f"Failed to retrieve extra projects information for organization {org_id}")
    
    # Developer Status Methods
    
    def get_developer_status(self) -> Dict:
        """
        Check if the user has developer API access.
        
        Returns:
            Dictionary with developer status information including:
            - user_id: ID of the user
            - has_developer_access: Whether the user has developer API access
            - pending_request: Whether there's a pending API access request
            - request_date: Date of the pending request (if applicable)
            
        Raises:
            requests.RequestException: If the API call fails
        """
        try:
            return self._make_request("GET", f"{self.user_url}/developer-status")
        except requests.RequestException as e:
            self._handle_request_error(e, "Failed to retrieve developer status")
    
    # Helper methods
    
    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format byte values into human-readable strings.
        
        Args:
            bytes_value: Number of bytes
            
        Returns:
            Human-readable string representation of the byte value
        """
        if not isinstance(bytes_value, (int, float)):
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if bytes_value < 1024 or unit == 'PB':
                return f"{bytes_value:.2f} {unit}" if unit != 'B' else f"{bytes_value} {unit}"
            bytes_value /= 1024
    
    def _handle_request_error(self, exception: Exception, message: str) -> None:
        """
        Handle request exceptions with more context.
        
        Args:
            exception: The caught exception
            message: Context message about what operation failed
            
        Raises:
            ValueError or RequestException with enhanced context
        """
        error_text = str(exception)
        
        # Check for common error types and provide more helpful messages
        if "401" in error_text:
            raise ValueError(f"{message}: Authentication failed. Please verify your API key and secret.")
        elif "403" in error_text:
            raise ValueError(f"{message}: Permission denied. You may not have access to this resource.")
        elif "404" in error_text:
            raise ValueError(f"{message}: Resource not found. Please verify the IDs you provided.")
        elif "429" in error_text:
            raise ValueError(f"{message}: Rate limit exceeded. Please reduce your request frequency.")
        else:
            # Re-raise with added context
            raise type(exception)(f"{message}: {error_text}")
