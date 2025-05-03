import os
import json
import requests
from typing import Dict, List, Optional, Union, Any, Literal, TypeVar, cast
from .base_client import BaseClient

class SettingsClient(BaseClient):
    """
    Client for interacting with Storylinez Settings API.
    Provides methods for managing user settings and temporary job storage.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the SettingsClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.settings_url = f"{self.base_url}/settings"
    
    # User Settings Management
    
    def get_settings(self) -> Dict:
        """
        Get all settings for the current user.
        
        Returns:
            Dictionary containing user settings (AI parameters, link preferences, UI preferences)
            
        Examples:
            >>> settings = client.settings.get_settings()
            >>> dark_mode = settings.get('ui_preferences', {}).get('dark_mode', False)
            >>> temperature = settings.get('ai_params', {}).get('temperature', 0.7)
        """
        return self._make_request("GET", f"{self.settings_url}/get")
    
    def save_settings(
        self,
        # AI parameters
        ai_params: Optional[Dict] = None,
        temperature: Optional[float] = None,
        iterations: Optional[int] = None,
        deepthink: Optional[bool] = None,
        web_search: Optional[bool] = None,
        overdrive: Optional[bool] = None,
        eco: Optional[bool] = None,
        # Link preferences
        link_preferences: Optional[Dict] = None,
        generate_thumbnail: Optional[bool] = None,
        generate_streamable: Optional[bool] = None,
        generate_download: Optional[bool] = None,
        detail: Optional[bool] = None,
        # UI preferences
        ui_preferences: Optional[Dict] = None,
        dark_mode: Optional[bool] = None,
        default_view: Optional[str] = None,
        language: Optional[str] = None,
        current_org_id: Optional[str] = None,
        last_project_id: Optional[str] = None,
        current_tab: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Save all settings for the current user. You can provide setting values either:
        1. As complete category dictionaries (ai_params, link_preferences, ui_preferences)
        2. As individual parameters which will be merged into their respective categories
        
        Args:
            ai_params: Complete AI parameters dictionary
            temperature: AI randomness parameter (0.0-1.0)
            iterations: Number of refinement iterations (positive integer)
            deepthink: Enable advanced thinking for complex topics
            web_search: Enable web search for up-to-date information
            overdrive: Enable maximum quality and detail
            eco: Enable eco mode for faster processing
            
            link_preferences: Complete link preferences dictionary
            generate_thumbnail: Generate thumbnail URLs when sharing
            generate_streamable: Generate streamable URLs when sharing
            generate_download: Generate download URLs when sharing
            detail: Include detailed information when sharing
            
            ui_preferences: Complete UI preferences dictionary
            dark_mode: Enable dark mode UI
            default_view: Default view mode for content displays (e.g., 'grid', 'list')
            language: Interface language code (ISO language code)
            current_org_id: ID of currently selected organization
            last_project_id: ID of last visited project
            current_tab: Current active tab in the UI (max 50 characters)
            
        Returns:
            Dictionary containing confirmation message and saved settings
            
        Raises:
            ValueError: If invalid parameters are provided
            
        Examples:
            >>> # Using category dictionaries
            >>> client.settings.save_settings(
            >>>     ai_params={"temperature": 0.8, "iterations": 4},
            >>>     ui_preferences={"dark_mode": True}
            >>> )
            >>> 
            >>> # Using individual parameters
            >>> client.settings.save_settings(
            >>>     temperature=0.8,
            >>>     dark_mode=True,
            >>>     language="fr"
            >>> )
        """
        # Initialize data with empty dictionaries for each category
        data: Dict[str, Any] = {}
        
        # Process AI parameters
        _ai_params = ai_params.copy() if ai_params is not None else {}
        
        if temperature is not None:
            if not 0 <= temperature <= 1:
                raise ValueError("Temperature must be between 0 and 1")
            _ai_params["temperature"] = temperature
            
        if iterations is not None:
            if not isinstance(iterations, int) or iterations < 1:
                raise ValueError("Iterations must be a positive integer")
            _ai_params["iterations"] = iterations
            
        if deepthink is not None:
            _ai_params["deepthink"] = bool(deepthink)
            
        if web_search is not None:
            _ai_params["web_search"] = bool(web_search)
            
        if overdrive is not None:
            _ai_params["overdrive"] = bool(overdrive)
            
        if eco is not None:
            _ai_params["eco"] = bool(eco)
            
        if eco and deepthink:
            print("Warning: Both 'eco' and 'deepthink' modes are enabled. These are typically mutually exclusive - enabling one may override the other.")
        
        if _ai_params:
            data["ai_params"] = _ai_params
        
        # Process link preferences
        _link_prefs = link_preferences.copy() if link_preferences is not None else {}
        
        if generate_thumbnail is not None:
            _link_prefs["generate_thumbnail"] = bool(generate_thumbnail)
            
        if generate_streamable is not None:
            _link_prefs["generate_streamable"] = bool(generate_streamable)
            
        if generate_download is not None:
            _link_prefs["generate_download"] = bool(generate_download)
            
        if detail is not None:
            _link_prefs["detail"] = bool(detail)
            
        if _link_prefs:
            data["link_preferences"] = _link_prefs
        
        # Process UI preferences
        _ui_prefs = ui_preferences.copy() if ui_preferences is not None else {}
        
        if dark_mode is not None:
            _ui_prefs["dark_mode"] = bool(dark_mode)
            
        if default_view is not None:
            _ui_prefs["default_view"] = str(default_view)
            
        if language is not None:
            _ui_prefs["language"] = str(language)
            
        if current_org_id is not None:
            _ui_prefs["current_org_id"] = str(current_org_id)
            
        if last_project_id is not None:
            _ui_prefs["last_project_id"] = str(last_project_id)
            
        if current_tab is not None:
            if len(current_tab) > 50:
                raise ValueError("current_tab must be 50 characters or less")
            _ui_prefs["current_tab"] = str(current_tab)
            
        if _ui_prefs:
            data["ui_preferences"] = _ui_prefs
            
        # Add any additional kwargs (for backwards compatibility or future expansion)
        if kwargs:
            for key, value in kwargs.items():
                if key not in data:  # Don't overwrite explicitly set parameters
                    data[key] = value
        
        # Validate that at least one category is being updated
        if not data:
            raise ValueError("At least one settings category (ai_params, link_preferences, or ui_preferences) must be provided")
            
        return self._make_request("POST", f"{self.settings_url}/save", json_data=data)
    
    def update_settings(
        self,
        # AI parameters
        ai_params: Optional[Dict] = None,
        temperature: Optional[float] = None,
        iterations: Optional[int] = None, 
        deepthink: Optional[bool] = None,
        web_search: Optional[bool] = None,
        overdrive: Optional[bool] = None,
        eco: Optional[bool] = None,
        # Link preferences
        link_preferences: Optional[Dict] = None,
        generate_thumbnail: Optional[bool] = None,
        generate_streamable: Optional[bool] = None,
        generate_download: Optional[bool] = None,
        detail: Optional[bool] = None,
        # UI preferences
        ui_preferences: Optional[Dict] = None,
        dark_mode: Optional[bool] = None,
        default_view: Optional[str] = None,
        language: Optional[str] = None,
        current_org_id: Optional[str] = None,
        last_project_id: Optional[str] = None,
        current_tab: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Update specific settings for the current user.
        Unlike save_settings, this method only updates the specified fields without replacing entire categories.
        
        Args:
            ai_params: AI parameters to update
            temperature: AI randomness parameter (0.0-1.0)
            iterations: Number of refinement iterations (positive integer)
            deepthink: Enable advanced thinking for complex topics
            web_search: Enable web search for up-to-date information
            overdrive: Enable maximum quality and detail
            eco: Enable eco mode for faster processing
            
            link_preferences: Link preferences to update
            generate_thumbnail: Generate thumbnail URLs when sharing
            generate_streamable: Generate streamable URLs when sharing
            generate_download: Generate download URLs when sharing
            detail: Include detailed information when sharing
            
            ui_preferences: UI preferences to update
            dark_mode: Enable dark mode UI
            default_view: Default view mode for content displays (e.g., 'grid', 'list')
            language: Interface language code (ISO language code)
            current_org_id: ID of currently selected organization
            last_project_id: ID of last visited project
            current_tab: Current active tab in the UI (max 50 characters)
            
        Returns:
            Dictionary containing confirmation message and updated fields
            
        Raises:
            ValueError: If invalid parameters are provided
            
        Examples:
            >>> # Using category dictionaries
            >>> client.settings.update_settings(
            >>>     ai_params={"temperature": 0.8},
            >>>     ui_preferences={"dark_mode": True}
            >>> )
            >>> 
            >>> # Using individual parameters
            >>> client.settings.update_settings(
            >>>     temperature=0.8,
            >>>     dark_mode=True
            >>> )
        """
        # This is similar to save_settings but using the update endpoint
        # Initialize data with empty dictionaries for each category
        data: Dict[str, Any] = {}
        
        # Process AI parameters
        _ai_params = ai_params.copy() if ai_params is not None else {}
        
        if temperature is not None:
            if not 0 <= temperature <= 1:
                raise ValueError("Temperature must be between 0 and 1")
            _ai_params["temperature"] = temperature
            
        if iterations is not None:
            if not isinstance(iterations, int) or iterations < 1:
                raise ValueError("Iterations must be a positive integer")
            _ai_params["iterations"] = iterations
            
        if deepthink is not None:
            _ai_params["deepthink"] = bool(deepthink)
            
        if web_search is not None:
            _ai_params["web_search"] = bool(web_search)
            
        if overdrive is not None:
            _ai_params["overdrive"] = bool(overdrive)
            
        if eco is not None:
            _ai_params["eco"] = bool(eco)
            
        if eco and deepthink:
            print("Warning: Both 'eco' and 'deepthink' modes are enabled. These are typically mutually exclusive - enabling one may override the other.")
        
        if _ai_params:
            data["ai_params"] = _ai_params
        
        # Process link preferences
        _link_prefs = link_preferences.copy() if link_preferences is not None else {}
        
        if generate_thumbnail is not None:
            _link_prefs["generate_thumbnail"] = bool(generate_thumbnail)
            
        if generate_streamable is not None:
            _link_prefs["generate_streamable"] = bool(generate_streamable)
            
        if generate_download is not None:
            _link_prefs["generate_download"] = bool(generate_download)
            
        if detail is not None:
            _link_prefs["detail"] = bool(detail)
            
        if _link_prefs:
            data["link_preferences"] = _link_prefs
        
        # Process UI preferences
        _ui_prefs = ui_preferences.copy() if ui_preferences is not None else {}
        
        if dark_mode is not None:
            _ui_prefs["dark_mode"] = bool(dark_mode)
            
        if default_view is not None:
            _ui_prefs["default_view"] = str(default_view)
            
        if language is not None:
            _ui_prefs["language"] = str(language)
            
        if current_org_id is not None:
            _ui_prefs["current_org_id"] = str(current_org_id)
            
        if last_project_id is not None:
            _ui_prefs["last_project_id"] = str(last_project_id)
            
        if current_tab is not None:
            if len(current_tab) > 50:
                raise ValueError("current_tab must be 50 characters or less")
            _ui_prefs["current_tab"] = str(current_tab)
            
        if _ui_prefs:
            data["ui_preferences"] = _ui_prefs
            
        # Add any additional kwargs (for backwards compatibility or future expansion)
        if kwargs:
            for key, value in kwargs.items():
                if key not in data:  # Don't overwrite explicitly set parameters
                    data[key] = value
        
        # Validate that at least one category is being updated
        if not data:
            raise ValueError("At least one settings category (ai_params, link_preferences, or ui_preferences) must be provided")
            
        return self._make_request("PUT", f"{self.settings_url}/update", json_data=data)
    
    def reset_settings(self, category: str = "all") -> Dict:
        """
        Reset all or specific settings categories to default values.
        
        Args:
            category: Settings category to reset. One of: "all", "ai_params", "link_preferences", "ui_preferences"
            
        Returns:
            Dictionary containing confirmation message and reset settings
            
        Raises:
            ValueError: If an invalid category is provided
            
        Examples:
            >>> # Reset all settings
            >>> client.settings.reset_settings()
            >>>
            >>> # Reset only AI parameters
            >>> client.settings.reset_settings(category="ai_params")
        """
        # Validate category
        valid_categories = ['all', 'ai_params', 'link_preferences', 'ui_preferences']
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
            
        return self._make_request("POST", f"{self.settings_url}/reset", json_data={"category": category})
    
    # Specialized Settings Updates
    
    def update_theme(self, dark_mode: bool) -> Dict:
        """
        Update UI theme preference (light/dark mode).
        
        Args:
            dark_mode: Whether to enable dark mode (True) or light mode (False)
            
        Returns:
            Dictionary containing confirmation message
            
        Examples:
            >>> # Enable dark mode
            >>> client.settings.update_theme(dark_mode=True)
            >>>
            >>> # Enable light mode
            >>> client.settings.update_theme(dark_mode=False)
        """
        if not isinstance(dark_mode, bool):
            dark_mode = bool(dark_mode)
            print(f"Warning: dark_mode parameter converted to boolean: {dark_mode}")
            
        return self._make_request("PUT", f"{self.settings_url}/theme", json_data={"dark_mode": dark_mode})
    
    def update_ai_defaults(
        self, 
        temperature: Optional[float] = None, 
        iterations: Optional[int] = None,
        deepthink: Optional[bool] = None, 
        overdrive: Optional[bool] = None,
        web_search: Optional[bool] = None, 
        eco: Optional[bool] = None
    ) -> Dict:
        """
        Update default AI parameters for content generation.
        
        Args:
            temperature: AI temperature parameter (0.0-1.0)
            iterations: Number of refinement iterations
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            
        Returns:
            Dictionary containing confirmation message and updated AI parameters
            
        Raises:
            ValueError: If invalid parameters are provided or no parameters specified
            
        Examples:
            >>> # Update temperature and enable web search
            >>> client.settings.update_ai_defaults(
            >>>     temperature=0.8,
            >>>     web_search=True
            >>> )
            >>>
            >>> # Switch to "deep thinking" mode
            >>> client.settings.update_ai_defaults(
            >>>     deepthink=True,
            >>>     eco=False,
            >>>     temperature=0.6
            >>> )
        """
        data = {}
        
        if temperature is not None:
            if not 0 <= temperature <= 1:
                raise ValueError("Temperature must be between 0 and 1")
            data["temperature"] = temperature
            
        if iterations is not None:
            if not isinstance(iterations, int) or iterations < 1:
                raise ValueError("Iterations must be a positive integer")
            data["iterations"] = iterations
            
        if deepthink is not None:
            data["deepthink"] = bool(deepthink)
            
        if overdrive is not None:
            data["overdrive"] = bool(overdrive)
            
        if web_search is not None:
            data["web_search"] = bool(web_search)
            
        if eco is not None:
            data["eco"] = bool(eco)
        
        if eco and deepthink and eco is True and deepthink is True:
            print("Warning: Both 'eco' and 'deepthink' modes are enabled. These are typically mutually exclusive - enabling one may override the other.")
            
        if not data:
            raise ValueError("At least one AI parameter must be provided")
            
        return self._make_request("PUT", f"{self.settings_url}/ai-defaults", json_data=data)
    
    # Temporary Job Management
    
    def add_job(
        self, 
        job_id: str, 
        job_type: str = "query_generation",
        org_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Add a temporary job to user storage for tracking asynchronous processes.
        
        Args:
            job_id: The unique ID of the job to store
            job_type: Type of job ("query_generation" or "search_recommendations")
            org_id: Organization ID (uses default if not provided)
            project_id: Optional project ID associated with the job
            metadata: Optional additional metadata about the job
            
        Returns:
            Dictionary containing confirmation message and entry ID
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Examples:
            >>> # Add a query generation job
            >>> client.settings.add_job(
            >>>     job_id="job_abc123", 
            >>>     job_type="query_generation",
            >>>     metadata={"query": "marketing video", "timestamp": "2023-07-29T10:15:00Z"}
            >>> )
            >>>
            >>> # Add a search recommendations job with project ID
            >>> client.settings.add_job(
            >>>     job_id="job_xyz456",
            >>>     job_type="search_recommendations",
            >>>     project_id="project_12345",
            >>>     metadata={"source_document": "doc_78901"}
            >>> )
        """
        # Validate job_id
        if not job_id or not isinstance(job_id, str):
            raise ValueError("job_id must be a non-empty string")
            
        # Use default org_id if not provided
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate job_type
        allowed_job_types = ["query_generation", "search_recommendations"]
        if job_type not in allowed_job_types:
            raise ValueError(f"job_type must be one of: {', '.join(allowed_job_types)}")
            
        data = {
            "job_id": job_id,
            "org_id": org_id,
            "job_type": job_type
        }
        
        if project_id:
            data["project_id"] = project_id
            
        if metadata:
            # Ensure metadata is a dictionary
            if not isinstance(metadata, dict):
                raise ValueError("metadata must be a dictionary")
            data["metadata"] = metadata
            
        return self._make_request("POST", f"{self.settings_url}/jobs/add", json_data=data)
    
    def list_jobs(
        self, 
        org_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        job_type: Optional[str] = None,
        page: int = 1, 
        limit: int = 10, 
        sort_by: str = "created_at", 
        sort_order: str = "desc"
    ) -> Dict:
        """
        List temporary jobs stored for the user with pagination support.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            project_id: Optional filter by project ID
            job_type: Optional filter by job type
            page: Page number for pagination (starts at 1)
            limit: Number of items per page (max value based on system configuration)
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            Dictionary with jobs list and pagination info
            
        Raises:
            ValueError: If parameters are invalid
            
        Examples:
            >>> # List all jobs for the default organization
            >>> all_jobs = client.settings.list_jobs()
            >>>
            >>> # Filter jobs by type and sort by creation date (ascending)
            >>> query_jobs = client.settings.list_jobs(
            >>>     job_type="query_generation",
            >>>     sort_order="asc"
            >>> )
            >>>
            >>> # Get page 2 with 5 jobs per page for a specific project
            >>> project_jobs = client.settings.list_jobs(
            >>>     project_id="project_12345",
            >>>     page=2,
            >>>     limit=5
            >>> )
        """
        # Use default org_id if not provided
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Validate page and limit
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
            
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
            
        # Validate sort_order
        if sort_order not in ["asc", "desc"]:
            raise ValueError("sort_order must be either 'asc' or 'desc'")
            
        # Validate job_type if provided
        if job_type and job_type not in ["query_generation", "search_recommendations"]:
            raise ValueError("job_type must be either 'query_generation' or 'search_recommendations'")
            
        params = {
            "org_id": org_id,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
        if project_id:
            params["project_id"] = project_id
            
        if job_type:
            params["job_type"] = job_type
            
        return self._make_request("GET", f"{self.settings_url}/jobs/list", params=params)
    
    def delete_job(self, job_id: str, org_id: Optional[str] = None) -> Dict:
        """
        Delete a temporary job from user storage.
        
        Args:
            job_id: ID of the job to delete
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary containing confirmation message
            
        Raises:
            ValueError: If job_id is invalid or org_id is missing
            
        Examples:
            >>> # Delete a job using the default organization ID
            >>> client.settings.delete_job("job_abc123")
            >>>
            >>> # Delete a job for a specific organization
            >>> client.settings.delete_job("job_xyz456", org_id="org_67890")
        """
        # Validate job_id
        if not job_id or not isinstance(job_id, str):
            raise ValueError("job_id must be a non-empty string")
            
        # Use default org_id if not provided
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        params = {
            "job_id": job_id,
            "org_id": org_id
        }
            
        return self._make_request("DELETE", f"{self.settings_url}/jobs/delete", params=params)
    
    def fetch_job_results(self, job_id: str, org_id: Optional[str] = None) -> Dict:
        """
        Fetch results for a temporary job from the build server.
        
        Args:
            job_id: ID of the job to fetch results for
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary containing job metadata and results
            
        Raises:
            ValueError: If job_id is invalid or org_id is missing
            
        Examples:
            >>> # Fetch results for a job
            >>> results = client.settings.fetch_job_results("job_abc123")
            >>> 
            >>> # Process results based on job type
            >>> if results.get("job_type") == "query_generation":
            >>>     items = results.get("result", {}).get("items", [])
            >>>     for item in items:
            >>>         print(f"Found: {item.get('title')} (Score: {item.get('score')})")
        """
        # Validate job_id
        if not job_id or not isinstance(job_id, str):
            raise ValueError("job_id must be a non-empty string")
            
        # Use default org_id if not provided
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        params = {
            "job_id": job_id,
            "org_id": org_id
        }
            
        return self._make_request("GET", f"{self.settings_url}/jobs/fetch_results", params=params)
    
    # Helper methods for common workflows
    
    def apply_preset(self, preset_name: str) -> Dict:
        """
        Apply a predefined settings preset to quickly configure multiple settings.
        
        Args:
            preset_name: Name of the preset to apply. One of: "default", "creative", "precise", 
                         "performance", "quality", "dark_theme", "light_theme"
                         
        Returns:
            Dictionary containing confirmation message and updated settings
            
        Raises:
            ValueError: If an invalid preset name is provided
            
        Examples:
            >>> # Apply creative preset for more varied outputs
            >>> client.settings.apply_preset("creative")
            >>>
            >>> # Apply dark theme preset
            >>> client.settings.apply_preset("dark_theme")
        """
        presets = {
            "default": {
                "ai_params": {
                    "eco": False,
                    "deepthink": False,
                    "temperature": 0.7,
                    "iterations": 3,
                    "web_search": False,
                    "overdrive": False
                },
                "ui_preferences": {
                    "dark_mode": False,
                    "default_view": "grid"
                }
            },
            "creative": {
                "ai_params": {
                    "temperature": 0.9,
                    "iterations": 4,
                    "deepthink": True,
                    "web_search": True,
                    "eco": False
                }
            },
            "precise": {
                "ai_params": {
                    "temperature": 0.3,
                    "iterations": 5,
                    "deepthink": True,
                    "web_search": True,
                    "eco": False
                }
            },
            "performance": {
                "ai_params": {
                    "eco": True,
                    "deepthink": False,
                    "iterations": 2,
                    "web_search": False,
                    "overdrive": False
                }
            },
            "quality": {
                "ai_params": {
                    "eco": False,
                    "deepthink": True,
                    "iterations": 5,
                    "overdrive": True
                }
            },
            "dark_theme": {
                "ui_preferences": {
                    "dark_mode": True
                }
            },
            "light_theme": {
                "ui_preferences": {
                    "dark_mode": False
                }
            }
        }
        
        if preset_name not in presets:
            raise ValueError(f"Invalid preset name. Must be one of: {', '.join(presets.keys())}")
        
        preset = presets[preset_name]
        
        # Apply the preset using the update_settings method
        print(f"Applying '{preset_name}' preset...")
        result = self.update_settings(**preset)
        print(f"Preset '{preset_name}' applied successfully.")
        
        return result
    
    def toggle_theme(self) -> Dict:
        """
        Toggle between dark mode and light mode.
        
        Returns:
            Dictionary containing confirmation message and new theme setting
            
        Examples:
            >>> # Toggle the current theme
            >>> client.settings.toggle_theme()
        """
        # First, get current settings
        settings = self.get_settings()
        
        # Get current dark_mode setting (default to False if not set)
        current_dark_mode = settings.get('ui_preferences', {}).get('dark_mode', False)
        
        # Toggle the setting
        new_dark_mode = not current_dark_mode
        
        # Update the theme
        print(f"Toggling theme from {'dark' if current_dark_mode else 'light'} to {'dark' if new_dark_mode else 'light'} mode...")
        result = self.update_theme(dark_mode=new_dark_mode)
        
        return result
    
    def backup_settings(self, filename: Optional[str] = None) -> str:
        """
        Back up current settings to a JSON file.
        
        Args:
            filename: Optional filename for the backup (default: storylinez_settings_YYYY-MM-DD.json)
            
        Returns:
            Path to the saved backup file
            
        Examples:
            >>> # Backup with default filename
            >>> backup_file = client.settings.backup_settings()
            >>> print(f"Settings backed up to {backup_file}")
            >>>
            >>> # Backup with custom filename
            >>> client.settings.backup_settings("my_settings_backup.json")
        """
        import datetime
        
        # Get current settings
        settings = self.get_settings()
        
        # Create default filename if not provided
        if filename is None:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f"storylinez_settings_{today}.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"Settings backed up to {filename}")
        return filename
    
    def restore_settings(self, filename: str) -> Dict:
        """
        Restore settings from a backup file.
        
        Args:
            filename: Path to the backup JSON file
            
        Returns:
            Dictionary containing confirmation message and restored settings
            
        Raises:
            FileNotFoundError: If the backup file doesn't exist
            json.JSONDecodeError: If the backup file isn't valid JSON
            KeyError: If the backup file doesn't contain required settings
            
        Examples:
            >>> # Restore from backup file
            >>> client.settings.restore_settings("storylinez_settings_2023-11-01.json")
        """
        # Load settings from file
        try:
            with open(filename, 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Backup file not found: {filename}")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Invalid JSON in backup file: {filename}")
        
        # Check if the backup contains settings
        required_keys = ["ai_params", "link_preferences", "ui_preferences"]
        missing_keys = [key for key in required_keys if key not in settings]
        if missing_keys:
            raise KeyError(f"Backup file is missing required settings: {', '.join(missing_keys)}")
        
        # Apply settings from backup
        print(f"Restoring settings from {filename}...")
        result = self.save_settings(
            ai_params=settings.get("ai_params"),
            link_preferences=settings.get("link_preferences"),
            ui_preferences=settings.get("ui_preferences")
        )
        
        print("Settings restored successfully!")
        return result
