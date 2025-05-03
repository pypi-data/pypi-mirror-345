import os
import json
import requests
import warnings
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from .base_client import BaseClient

class StoryboardClient(BaseClient):
    """
    Client for interacting with Storylinez Storyboard API.
    Provides methods for creating and managing storyboards, editing storyboard content, and retrieving history.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinez.com", default_org_id: str = None):
        """
        Initialize the StoryboardClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.storyboard_url = f"{self.base_url}/storyboard"
    
    # Storyboard Creation and Management
    
    def create_storyboard(
        self, 
        project_id: str, 
        deepthink: bool = False, 
        overdrive: bool = False, 
        web_search: bool = False, 
        eco: bool = False, 
        temperature: float = 0.7, 
        iterations: int = 3, 
        full_length: Optional[int] = None, 
        voiceover_mode: str = "generated", 
        skip_voiceover: bool = False,
        documents: Union[None, str, List[str]] = None,
        **kwargs
    ) -> Dict:
        """
        Create a new storyboard for a project.
        
        Args:
            project_id: ID of the project to create the storyboard for
            deepthink: Enable advanced thinking for complex topics (improves narrative coherence)
            overdrive: Enable maximum quality and detail (uses more resources)
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing (lower quality but faster)
            temperature: AI temperature parameter (0.0-1.0) - lower is more deterministic, higher is more creative
            iterations: Number of refinement iterations (1-10) - higher values yield more refined results
            full_length: Target length of the video in seconds
            voiceover_mode: Voiceover mode ('generated' or 'uploaded')
            skip_voiceover: Whether to skip generating voiceover
            documents: List of document IDs or a single document ID to include in the storyboard
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the created storyboard details and job information
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
        """
        if not project_id:
            raise ValueError("project_id is required")
            
        # Parameter validation and conversion
        try:
            temperature = float(temperature)
            if not 0.0 <= temperature <= 1.0:
                warnings.warn(f"Temperature {temperature} is outside the recommended range (0.0-1.0). Clamping to valid range.")
                temperature = max(0.0, min(1.0, temperature))
        except (TypeError, ValueError):
            raise ValueError("temperature must be a float between 0.0 and 1.0")
            
        try:
            iterations = int(iterations)
            if iterations < 1:
                warnings.warn("iterations must be at least 1. Setting to 1.")
                iterations = 1
            elif iterations > 10:
                warnings.warn("iterations > 10 may result in longer processing times. Consider a lower value.")
        except (TypeError, ValueError):
            raise ValueError("iterations must be an integer")
                
        if full_length is not None:
            try:
                full_length = int(full_length)
                if full_length <= 0:
                    raise ValueError("full_length must be a positive integer")
            except (TypeError, ValueError):
                raise ValueError("full_length must be a positive integer")
                
        voiceover_mode = str(voiceover_mode).lower()
        if voiceover_mode not in ["generated", "uploaded"]:
            raise ValueError("voiceover_mode must be either 'generated' or 'uploaded'")
            
        if voiceover_mode == "uploaded":
            # Check if the project has a voiceover file uploaded
            warnings.warn("Make sure your project has a voiceover file uploaded when using 'uploaded' mode.")
        
        data = {
            "project_id": project_id,
            "deepthink": bool(deepthink),
            "overdrive": bool(overdrive),
            "web_search": bool(web_search),
            "eco": bool(eco),
            "temperature": temperature,
            "iterations": iterations,
            "voiceover_mode": voiceover_mode,
            "skip_voiceover": bool(skip_voiceover)
        }
        
        if full_length is not None:
            data["full_length"] = full_length
            
        # Ensure documents is always a list of strings if provided
        if documents is not None:
            if isinstance(documents, str):
                data["documents"] = [documents]
            elif isinstance(documents, list):
                data["documents"] = documents
            else:
                data["documents"] = []
            
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
        
        params = {"include_details": "false"}
        return self._make_request("POST", f"{self.storyboard_url}/create", params=params, json_data=data)
    
    def get_storyboard(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        include_results: bool = False, 
        include_details: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get a storyboard by ID or project ID.
        
        Args:
            storyboard_id: ID of the storyboard to retrieve (either this or project_id must be provided)
            project_id: ID of the project to retrieve the storyboard for (either this or storyboard_id must be provided)
            include_results: Whether to include job results (may return large response)
            include_details: Whether to include media details (stock videos, audio, etc.)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the storyboard details
            
        Raises:
            ValueError: If neither storyboard_id nor project_id is provided
            requests.exceptions.RequestException: If the API request fails
        """
        if not storyboard_id and not project_id:
            raise ValueError("Either storyboard_id or project_id must be provided")
            
        params = {
            "include_results": str(bool(include_results)).lower(),
            "include_details": str(bool(include_details)).lower()
        }
        
        if storyboard_id:
            params["storyboard_id"] = storyboard_id
        if project_id:
            params["project_id"] = project_id
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value
            
        return self._make_request("GET", f"{self.storyboard_url}/get", params=params)
    
    def update_storyboard(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        update_ai_params: bool = True,
        **kwargs
    ) -> Dict:
        """
        Update a storyboard with the latest project and prompt data.
        
        Args:
            storyboard_id: ID of the storyboard to update (either this or project_id must be provided)
            project_id: ID of the project whose storyboard to update (either this or storyboard_id must be provided)
            update_ai_params: Whether to update AI parameters from the project's prompt
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the updated storyboard
            
        Raises:
            ValueError: If neither storyboard_id nor project_id is provided
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            After updating, the storyboard will be marked as 'stale' and will need to be regenerated
            using the redo_storyboard method to incorporate the updates.
        """
        if not storyboard_id and not project_id:
            raise ValueError("Either storyboard_id or project_id must be provided")
            
        data = {"update_ai_params": bool(update_ai_params)}
        
        if storyboard_id:
            data["storyboard_id"] = storyboard_id
        if project_id:
            data["project_id"] = project_id
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("PUT", f"{self.storyboard_url}/selfupdate", json_data=data)
    
    def update_storyboard_values(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        edited_storyboard: Optional[Dict] = None, 
        regeneration_prompt: Optional[str] = None,
        deepthink: Optional[bool] = None, 
        overdrive: Optional[bool] = None, 
        web_search: Optional[bool] = None, 
        eco: Optional[bool] = None,
        temperature: Optional[float] = None, 
        iterations: Optional[int] = None, 
        full_length: Optional[int] = None, 
        skip_voiceover: Optional[bool] = None,
        voiceover_mode: Optional[str] = None,
        documents: Union[None, str, List[str]] = None,
        **kwargs
    ) -> Dict:
        """
        Update specific values in a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard to update (either this or project_id must be provided)
            project_id: ID of the project whose storyboard to update (either this or storyboard_id must be provided)
            edited_storyboard: Updated storyboard data structure (must conform to the storyboard schema)
            regeneration_prompt: Prompt to guide regeneration (instructions for the AI when regenerating)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            temperature: AI temperature parameter (0.0-1.0)
            iterations: Number of refinement iterations (1-10)
            full_length: Target length of the video in seconds
            skip_voiceover: Whether to skip generating voiceover
            voiceover_mode: Voiceover mode ('generated' or 'uploaded')
            documents: List of document IDs or a single document ID to include in the storyboard
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the updated storyboard
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            After updating values, the storyboard will be marked as 'stale' and will need to be 
            regenerated using the redo_storyboard method to incorporate the updates.
        """
        if not storyboard_id and not project_id:
            raise ValueError("Either storyboard_id or project_id must be provided")
            
        data = {}
        
        if storyboard_id:
            data["storyboard_id"] = storyboard_id
        if project_id:
            data["project_id"] = project_id
            
        # Parameter validation and conversion
        if edited_storyboard is not None:
            if not isinstance(edited_storyboard, dict):
                raise ValueError("edited_storyboard must be a dictionary that conforms to the storyboard schema")
            data["edited_storyboard"] = edited_storyboard
            
        if regeneration_prompt is not None:
            if not regeneration_prompt.strip():
                warnings.warn("Empty regeneration_prompt was provided. This may not have the expected effect.")
            data["regeneration_prompt"] = str(regeneration_prompt)
            
        if deepthink is not None:
            data["deepthink"] = bool(deepthink)
            
        if overdrive is not None:
            data["overdrive"] = bool(overdrive)
            
        if web_search is not None:
            data["web_search"] = bool(web_search)
            
        if eco is not None:
            data["eco"] = bool(eco)
            
        if temperature is not None:
            try:
                temperature = float(temperature)
                if not 0.0 <= temperature <= 1.0:
                    warnings.warn(f"Temperature {temperature} is outside the recommended range (0.0-1.0). Clamping to valid range.")
                    temperature = max(0.0, min(1.0, temperature))
                data["temperature"] = temperature
            except (TypeError, ValueError):
                raise ValueError("temperature must be a float between 0.0 and 1.0")
            
        if iterations is not None:
            try:
                iterations = int(iterations)
                if iterations < 1:
                    warnings.warn("iterations must be at least 1. Setting to 1.")
                    iterations = 1
                elif iterations > 10:
                    warnings.warn("iterations > 10 may result in longer processing times. Consider a lower value.")
                data["iterations"] = iterations
            except (TypeError, ValueError):
                raise ValueError("iterations must be an integer")
            
        if full_length is not None:
            try:
                full_length = int(full_length)
                if full_length <= 0:
                    raise ValueError("full_length must be a positive integer")
                data["full_length"] = full_length
            except (TypeError, ValueError):
                raise ValueError("full_length must be a positive integer")
            
        if skip_voiceover is not None:
            data["skip_voiceover"] = bool(skip_voiceover)
            
        if voiceover_mode is not None:
            voiceover_mode = str(voiceover_mode).lower()
            if voiceover_mode not in ["generated", "uploaded"]:
                raise ValueError("voiceover_mode must be either 'generated' or 'uploaded'")
            data["voiceover_mode"] = voiceover_mode
            
            if voiceover_mode == "uploaded":
                warnings.warn("Make sure your project has a voiceover file uploaded when using 'uploaded' mode.")
        
        if documents is not None:
            if isinstance(documents, str):
                data["documents"] = [documents]
            elif isinstance(documents, list):
                data["documents"] = documents
            else:
                data["documents"] = []
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("PUT", f"{self.storyboard_url}/update", json_data=data)
    
    def redo_storyboard(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None, 
        include_history: bool = False,
        **kwargs
    ) -> Dict:
        """
        Redo a storyboard generation job.
        
        Args:
            storyboard_id: ID of the storyboard to redo (either this or project_id must be provided)
            project_id: ID of the project whose storyboard to redo (either this or storyboard_id must be provided)
            include_history: Whether to include history as context for regeneration (provides AI with more context)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with job information
            
        Raises:
            ValueError: If neither storyboard_id nor project_id is provided
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            This method will clear any edited_storyboard and regeneration_prompt values,
            but will use them for context in the new generation before clearing them.
        """
        if not storyboard_id and not project_id:
            raise ValueError("Either storyboard_id or project_id must be provided")
            
        data = {"include_history": bool(include_history)}
        
        if storyboard_id:
            data["storyboard_id"] = storyboard_id
        if project_id:
            data["project_id"] = project_id
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("POST", f"{self.storyboard_url}/redo", json_data=data)
    
    # Storyboard Content Editing
    
    def reorder_storyboard_items(
        self, 
        storyboard_id: str, 
        array_type: str, 
        new_order: List[int],
        **kwargs
    ) -> Dict:
        """
        Reorder items in a storyboard array.
        
        Args:
            storyboard_id: ID of the storyboard to update
            array_type: Type of array to reorder ('videos' or 'background_music')
            new_order: List of indices in the new order
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            The new_order must contain all indices from 0 to n-1 where n is the 
            number of items in the array, with no duplicates.
        """
        if not storyboard_id:
            raise ValueError("storyboard_id is required")
            
        array_type = str(array_type).lower()
        if array_type not in ['videos', 'background_music']:
            raise ValueError("array_type must be either 'videos' or 'background_music'")
            
        if not isinstance(new_order, list):
            raise ValueError("new_order must be a list of integers")
            
        # Validate that new_order contains integers
        validated_order = []
        for i, idx in enumerate(new_order):
            try:
                validated_order.append(int(idx))
            except (TypeError, ValueError):
                raise ValueError(f"new_order[{i}] is not a valid integer: {idx}")
                
        # Check for duplicates
        if len(validated_order) != len(set(validated_order)):
            raise ValueError("new_order contains duplicate indices")
            
        data = {
            "storyboard_id": storyboard_id,
            "array_type": array_type,
            "new_order": validated_order
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("PUT", f"{self.storyboard_url}/reorder", json_data=data)
    
    def edit_storyboard_item(
        self, 
        storyboard_id: str, 
        item_type: str, 
        updated_item: Dict,
        item_index: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """
        Edit an item in a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard to update
            item_type: Type of item to edit ('videos', 'background_music', or 'voiceover')
            updated_item: Updated item data structure
            item_index: Index of the item to update (required for 'videos' and 'background_music')
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            For 'videos' and 'background_music', item_index is required.
            For 'voiceover', item_index is not used as there is only one voiceover object.
        """
        if not storyboard_id:
            raise ValueError("storyboard_id is required")
            
        if not updated_item:
            raise ValueError("updated_item is required and cannot be empty")
            
        item_type = str(item_type).lower()
        if item_type not in ['videos', 'background_music', 'voiceover']:
            raise ValueError("item_type must be one of: 'videos', 'background_music', 'voiceover'")
            
        if item_type != 'voiceover' and item_index is None:
            raise ValueError(f"item_index is required for item_type '{item_type}'")
            
        if not isinstance(updated_item, dict):
            raise ValueError("updated_item must be a dictionary")
            
        # Validate required fields for different item types
        if item_type in ['videos', 'background_music']:
            if 'dir' not in updated_item:
                raise ValueError(f"updated_item for {item_type} must contain a 'dir' field with the media path")
                
        if item_type == 'voiceover' and 'transcription' not in updated_item:
            warnings.warn("No 'transcription' found in voiceover data. This might affect the quality of the voiceover.")
            
        data = {
            "storyboard_id": storyboard_id,
            "item_type": item_type,
            "updated_item": updated_item
        }
        
        if item_index is not None:
            try:
                data["item_index"] = int(item_index)
            except (TypeError, ValueError):
                raise ValueError("item_index must be an integer")
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("PUT", f"{self.storyboard_url}/edit/item", json_data=data)
    
    def change_storyboard_media(
        self, 
        storyboard_id: str, 
        item_type: str, 
        item_index: int,
        file_id: Optional[str] = None, 
        stock_id: Optional[str] = None, 
        path: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Change media for an item in a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard to update
            item_type: Type of item to update ('videos' or 'background_music')
            item_index: Index of the item to update
            file_id: ID of the file to use (one of file_id, stock_id, or path must be provided)
            stock_id: ID of the stock media to use (one of file_id, stock_id, or path must be provided)
            path: Direct path to the media file (one of file_id, stock_id, or path must be provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            Exactly one of file_id, stock_id, or path must be provided.
            For 'videos', both video and image files are accepted.
            For 'background_music', only audio files are accepted.
        """
        if not storyboard_id:
            raise ValueError("storyboard_id is required")
            
        item_type = str(item_type).lower()
        if item_type not in ['videos', 'background_music']:
            raise ValueError("item_type must be either 'videos' or 'background_music'")
            
        try:
            item_index = int(item_index)
        except (TypeError, ValueError):
            raise ValueError("item_index must be an integer")
            
        source_count = sum(1 for x in [file_id, stock_id, path] if x)
        if source_count == 0:
            raise ValueError("One of file_id, stock_id, or path must be provided")
        elif source_count > 1:
            raise ValueError("Only one of file_id, stock_id, or path should be provided")
            
        if item_type == 'background_music' and file_id:
            warnings.warn("Make sure the file_id references an audio file when using 'background_music' type")
            
        data = {
            "storyboard_id": storyboard_id,
            "item_type": item_type,
            "item_index": item_index
        }
        
        if file_id:
            data["file_id"] = str(file_id)
        elif stock_id:
            data["stock_id"] = str(stock_id)
        elif path:
            data["path"] = str(path)
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            
        return self._make_request("PUT", f"{self.storyboard_url}/change_media", json_data=data)
    
    # Storyboard History and Media
    
    def get_storyboard_history(
        self, 
        storyboard_id: str, 
        page: int = 1, 
        limit: int = 10,
        history_type: Optional[str] = None, 
        include_current: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get history of changes for a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard
            page: Page number for pagination (starts from 1)
            limit: Number of items per page
            history_type: Filter by history type ('update', 'generation', 'prompt', 'selfupdate', 'media_change')
            include_current: Whether to include the current state as a history entry
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with history entries
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            History entries are returned in reverse chronological order (newest first).
        """
        if not storyboard_id:
            raise ValueError("storyboard_id is required")
            
        try:
            page = int(page)
            if page < 1:
                warnings.warn("page should be >= 1, setting to 1")
                page = 1
        except (TypeError, ValueError):
            raise ValueError("page must be a positive integer")
            
        try:
            limit = int(limit)
            if limit < 1:
                warnings.warn("limit should be >= 1, setting to 10")
                limit = 10
            elif limit > 100:
                warnings.warn("limit > 100 may result in large responses. Consider a lower value.")
        except (TypeError, ValueError):
            raise ValueError("limit must be a positive integer")
            
        if history_type is not None:
            history_type = str(history_type).lower()
            if history_type not in ['update', 'generation', 'prompt', 'selfupdate', 'media_change']:
                warnings.warn(f"history_type '{history_type}' is not a standard type. Filter may not work as expected.")
            
        params = {
            "storyboard_id": storyboard_id,
            "page": page,
            "limit": limit,
            "include_current": str(bool(include_current)).lower()
        }
        
        if history_type:
            params["history_type"] = history_type
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value
            
        return self._make_request("GET", f"{self.storyboard_url}/history", params=params)
    
    def get_storyboard_media(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        include_analysis: bool = False, 
        generate_thumbnail: bool = True,
        generate_streamable: bool = True, 
        generate_download: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get media files used in a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard (either this or project_id must be provided)
            project_id: ID of the project (either this or storyboard_id must be provided)
            include_analysis: Whether to include detailed analysis data (may result in large responses)
            generate_thumbnail: Whether to generate thumbnail URLs for videos/images
            generate_streamable: Whether to generate streamable URLs for videos/audio
            generate_download: Whether to generate download URLs (enabling increases API response time)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with media files grouped by type (videos, background_music, voiceover)
            
        Raises:
            ValueError: If neither storyboard_id nor project_id is provided
            requests.exceptions.RequestException: If the API request fails
            
        Note:
            The response includes media type counts and URLs for accessing the media.
        """
        if not storyboard_id and not project_id:
            raise ValueError("Either storyboard_id or project_id must be provided")
            
        params = {
            "include_analysis": str(bool(include_analysis)).lower(),
            "generate_thumbnail": str(bool(generate_thumbnail)).lower(),
            "generate_streamable": str(bool(generate_streamable)).lower(),
            "generate_download": str(bool(generate_download)).lower()
        }
        
        if storyboard_id:
            params["storyboard_id"] = storyboard_id
        if project_id:
            params["project_id"] = project_id
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value
            
        return self._make_request("GET", f"{self.storyboard_url}/media_involved", params=params)
    
    # Convenience and Workflow Methods
    
    def update_and_regenerate(
        self, 
        storyboard_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        regeneration_prompt: Optional[str] = None,
        update_ai_params: bool = True, 
        include_history: bool = True
    ) -> Dict:
        """
        Convenience method that updates a storyboard with latest project data and then regenerates it.
        
        Args:
            storyboard_id: ID of the storyboard (either this or project_id must be provided)
            project_id: ID of the project (either this or storyboard_id must be provided)
            regeneration_prompt: Optional prompt to guide the regeneration
            update_ai_params: Whether to update AI parameters from the project's prompt
            include_history: Whether to include history as context for regeneration
            
        Returns:
            Dictionary with the job information for the regeneration
            
        Raises:
            ValueError: If neither storyboard_id nor project_id is provided
            requests.exceptions.RequestException: If the API request fails
        """
        # First, update the storyboard (if regeneration_prompt is provided, add it)
        update_params = {}
        if regeneration_prompt:
            # Add the regeneration prompt to a separate update call
            if storyboard_id:
                update_params["storyboard_id"] = storyboard_id
            else:
                update_params["project_id"] = project_id
            
            self.update_storyboard_values(
                regeneration_prompt=regeneration_prompt, 
                **update_params
            )
            
        # Then update with latest data
        result = self.update_storyboard(
            storyboard_id=storyboard_id,
            project_id=project_id,
            update_ai_params=update_ai_params
        )
        
        # Get the storyboard_id from the result if we only had project_id
        if not storyboard_id and project_id:
            storyboard_id = result.get("storyboard", {}).get("storyboard_id")
            
        # Now regenerate the storyboard
        return self.redo_storyboard(
            storyboard_id=storyboard_id,
            include_history=include_history
        )
        
    def wait_for_generation_complete(
        self, 
        job_id: str, 
        polling_interval: int = 5, 
        timeout: int = 300
    ) -> Dict:
        """
        Wait for a storyboard generation job to complete, polling at regular intervals.
        
        Args:
            job_id: The job ID returned from create_storyboard or redo_storyboard
            polling_interval: Time in seconds between status checks
            timeout: Maximum time to wait in seconds
            
        Returns:
            The completed job result
            
        Raises:
            TimeoutError: If the job doesn't complete within the timeout period
            requests.exceptions.RequestException: If the API request fails
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Use a direct API call to the job status endpoint
            response = requests.get(
                f"{self.base_url}/build/getjob", 
                params={'job_id': job_id},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                job_data = response.json()
                status = job_data.get('status')
                
                if status == "COMPLETED":
                    return job_data
                elif status in ["FAILED", "ERROR"]:
                    raise Exception(f"Job failed with status: {status}, message: {job_data.get('message', 'No message')}")
                    
            time.sleep(polling_interval)
            
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
    
    def create_storyboard_and_wait(
        self, 
        project_id: str, 
        polling_interval: int = 5, 
        timeout: int = 300, 
        **kwargs
    ) -> Dict:
        """
        Creates a new storyboard and waits for its completion.
        
        Args:
            project_id: ID of the project to create the storyboard for
            polling_interval: Time in seconds between status checks
            timeout: Maximum time to wait in seconds
            **kwargs: Additional parameters to pass to create_storyboard
            
        Returns:
            Dictionary with the complete storyboard information
            
        Raises:
            TimeoutError: If the job doesn't complete within the timeout period
            requests.exceptions.RequestException: If the API request fails
        """
        # Create the storyboard
        result = self.create_storyboard(project_id=project_id, **kwargs)
        job_id = result.get("job_id")
        
        if not job_id:
            raise ValueError("No job_id found in create_storyboard response")
            
        # Wait for completion
        job_result = self.wait_for_generation_complete(
            job_id=job_id,
            polling_interval=polling_interval,
            timeout=timeout
        )
        
        # Get the storyboard with the updated results
        storyboard_id = result.get("storyboard", {}).get("storyboard_id")
        if not storyboard_id:
            raise ValueError("No storyboard_id found in create_storyboard response")
            
        return self.get_storyboard(storyboard_id=storyboard_id, include_results=True)
        
    def create_simple_edit(
        self, 
        storyboard_id: str, 
        scene_changes: Dict[int, Dict]
    ) -> Dict:
        """
        Helper method to make simple edits to multiple scenes in a storyboard.
        
        Args:
            storyboard_id: ID of the storyboard to edit
            scene_changes: Dictionary mapping scene indices to changes to make
                           (e.g., {0: {"scene": "New Title"}, 2: {"details": "New description"}})
            
        Returns:
            Dictionary with the operation result
            
        Raises:
            ValueError: If parameters are invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Get the current storyboard
        storyboard = self.get_storyboard(storyboard_id=storyboard_id, include_results=True)
        
        # Get the current storyboard data
        edited_storyboard = storyboard.get("edited_storyboard")
        if not edited_storyboard:
            # Try to get from job results
            if "old_job_result" in storyboard and "results" in storyboard["old_job_result"]:
                edited_storyboard = storyboard["old_job_result"]["results"]
            else:
                raise ValueError("No storyboard data available to edit")
                
        # Make a deep copy to avoid modifying the original
        import copy
        edited_data = copy.deepcopy(edited_storyboard)
        
        # Make changes to each scene
        videos = edited_data.get("videos", [])
        for idx, changes in scene_changes.items():
            if not isinstance(idx, int) or idx < 0 or idx >= len(videos):
                warnings.warn(f"Scene index {idx} is out of range. Skipping changes.")
                continue
                
            # Update the scene with the provided changes
            for key, value in changes.items():
                videos[idx][key] = value
                
        # Update the videos array in the edited data
        edited_data["videos"] = videos
        
        # Update the storyboard with the new edited_storyboard
        return self.update_storyboard_values(
            storyboard_id=storyboard_id,
            edited_storyboard=edited_data
        )
