import os
import json
import requests
import warnings
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from .base_client import BaseClient

class SequenceClient(BaseClient):
    """
    Client for interacting with Storylinez Sequence API.
    Provides methods for creating, retrieving, and managing sequences for video generation.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the SequenceClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.sequence_url = f"{self.base_url}/sequence"
    
    # Sequence Creation and Retrieval
    
    def create_sequence(
        self, 
        project_id: str, 
        apply_template: bool = False, 
        apply_grade: bool = False, 
        grade_type: str = "single",
        orientation: str = None, 
        deepthink: bool = False, 
        overdrive: bool = False, 
        web_search: bool = False, 
        eco: bool = False, 
        temperature: float = 0.7, 
        iterations: int = 1,
        **kwargs
    ) -> Dict:
        """
        Create a new sequence for a project.
        
        Args:
            project_id: ID of the project to create the sequence for
            apply_template: Whether to apply a template to the sequence
            apply_grade: Whether to apply color grading to the sequence
            grade_type: Type of grading to apply ("single" or "multi")
            orientation: Video orientation ("landscape", "portrait", or "square") - defaults to project setting
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            temperature: AI temperature parameter (0.0-1.0)
            iterations: Number of refinement iterations
            
        Returns:
            Dictionary with the created sequence details and job information
        
        Raises:
            ValueError: For invalid parameter values
            Exception: If API request fails
        """
        if not project_id:
            raise ValueError("project_id is required")
        
        # Validate grade_type
        if grade_type not in ["single", "multi"]:
            raise ValueError("grade_type must be either 'single' or 'multi'")
        
        # Validate orientation if provided
        if orientation and orientation not in ["landscape", "portrait", "square"]:
            raise ValueError("orientation must be one of: 'landscape', 'portrait', 'square'")
        
        # Validate temperature range
        if not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
        
        # Validate iterations
        if iterations < 1:
            raise ValueError("iterations must be at least 1")
        
        # Display helpful tips based on settings
        if deepthink and temperature < 0.5:
            warnings.warn("Using deepthink with low temperature (<0.5) may result in very conservative outputs.")
        
        if overdrive and eco:
            warnings.warn("'overdrive' and 'eco' modes have opposite effects. Consider using only one.")
        
        data = {
            "project_id": project_id,
            "apply_template": apply_template,
            "apply_grade": apply_grade,
            "grade_type": grade_type,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "web_search": web_search,
            "eco": eco,
            "temperature": float(temperature),  # Ensure it's a float
            "iterations": int(iterations)       # Ensure it's an integer
        }
        
        if orientation:
            data["orientation"] = orientation
            
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.sequence_url}/create", json_data=data)
    
    def get_sequence(
        self, 
        sequence_id: str = None, 
        project_id: str = None,
        include_results: bool = True, 
        include_storyboard: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get details of a sequence by either sequence ID or project ID.
        
        Args:
            sequence_id: ID of the sequence to retrieve (either this or project_id must be provided)
            project_id: ID of the project to retrieve the sequence for (either this or sequence_id must be provided)
            include_results: Whether to include job results
            include_storyboard: Whether to include the storyboard data
            
        Returns:
            Dictionary with sequence details
            
        Raises:
            ValueError: If neither sequence_id nor project_id is provided
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
            
        params = {
            "include_results": str(include_results).lower(),
            "include_storyboard": str(include_storyboard).lower()
        }
        
        if sequence_id:
            params["sequence_id"] = sequence_id
        if project_id:
            params["project_id"] = project_id
            
        # Add any additional kwargs for backward compatibility
        params.update(kwargs)
            
        return self._make_request("GET", f"{self.sequence_url}/get", params=params)
    
    def redo_sequence(
        self, 
        sequence_id: str = None, 
        project_id: str = None,
        include_history: bool = False, 
        regenerate_prompt: str = None,
        **kwargs
    ) -> Dict:
        """
        Regenerate a sequence with the latest storyboard data.
        
        Args:
            sequence_id: ID of the sequence to regenerate (either this or project_id must be provided)
            project_id: ID of the project whose sequence to regenerate (either this or sequence_id must be provided)
            include_history: Whether to include sequence history as context for regeneration
            regenerate_prompt: Optional prompt to guide the regeneration
            
        Returns:
            Dictionary with the regeneration job details
            
        Raises:
            ValueError: If neither sequence_id nor project_id is provided
            
        Tips:
            - Use regenerate_prompt to guide the AI on what to improve or change
            - Examples: "Make transitions smoother", "Focus more on product close-ups"
            - Setting include_history=True helps the AI understand previous attempts
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
            
        data = {"include_history": include_history}
        
        if sequence_id:
            data["sequence_id"] = sequence_id
        if project_id:
            data["project_id"] = project_id
        if regenerate_prompt:
            data["regenerate_prompt"] = regenerate_prompt
            
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
            
        return self._make_request("POST", f"{self.sequence_url}/redo", json_data=data)
    
    def update_sequence(
        self, 
        sequence_id: str = None, 
        project_id: str = None, 
        update_ai_params: bool = True,
        **kwargs
    ) -> Dict:
        """
        Update a sequence with the latest storyboard and voiceover data without regenerating it.
        This is useful when upstream components like storyboard or voiceover have changed.
        
        Args:
            sequence_id: ID of the sequence to update (either this or project_id must be provided)
            project_id: ID of the project whose sequence to update (either this or sequence_id must be provided)
            update_ai_params: Whether to update AI parameters from the project's storyboard
            
        Returns:
            Dictionary with update confirmation
            
        Raises:
            ValueError: If neither sequence_id nor project_id is provided
            
        Notes:
            This method only updates the sequence with the latest data but does not regenerate it.
            To regenerate the sequence after updating, use redo_sequence().
            Typical workflow: modify storyboard → update_sequence() → redo_sequence()
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
            
        data = {"update_ai_params": update_ai_params}
        
        if sequence_id:
            data["sequence_id"] = sequence_id
        if project_id:
            data["project_id"] = project_id
            
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
            
        return self._make_request("PUT", f"{self.sequence_url}/selfupdate", json_data=data)
    
    def update_sequence_settings(
        self,
        sequence_id: str = None, 
        project_id: str = None,
        apply_template: bool = None, 
        apply_grade: bool = None,
        grade_type: str = None, 
        orientation: str = None,
        deepthink: bool = None, 
        overdrive: bool = None,
        web_search: bool = None, 
        eco: bool = None,
        temperature: float = None, 
        iterations: int = None,
        regenerate_prompt: str = None, 
        edited_sequence: Dict = None,
        **kwargs
    ) -> Dict:
        """
        Update sequence settings without regenerating.
        
        Args:
            sequence_id: ID of the sequence to update (either this or project_id must be provided)
            project_id: ID of the project whose sequence to update (either this or sequence_id must be provided)
            apply_template: Whether to apply a template to the sequence
            apply_grade: Whether to apply color grading to the sequence
            grade_type: Type of grading to apply ("single" or "multi")
            orientation: Video orientation ("landscape", "portrait", or "square")
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            temperature: AI temperature parameter (0.0-1.0)
            iterations: Number of refinement iterations
            regenerate_prompt: Optional prompt to guide regeneration
            edited_sequence: Complete edited sequence structure
            
        Returns:
            Dictionary with the update confirmation
            
        Raises:
            ValueError: If neither sequence_id nor project_id is provided or for invalid parameters
            
        Notes:
            Changes are only saved but not applied - use redo_sequence() after updating to regenerate
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
        
        # Validate parameters if provided
        if grade_type is not None and grade_type not in ["single", "multi"]:
            raise ValueError("grade_type must be either 'single' or 'multi'")
        
        if orientation is not None and orientation not in ["landscape", "portrait", "square"]:
            raise ValueError("orientation must be one of: 'landscape', 'portrait', 'square'")
        
        if temperature is not None and not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
        
        if iterations is not None and iterations < 1:
            raise ValueError("iterations must be at least 1")
            
        data = {}
        
        if sequence_id:
            data["sequence_id"] = sequence_id
        if project_id:
            data["project_id"] = project_id
        if apply_template is not None:
            data["apply_template"] = apply_template
        if apply_grade is not None:
            data["apply_grade"] = apply_grade
        if grade_type is not None:
            data["grade_type"] = grade_type
        if orientation is not None:
            data["orientation"] = orientation
        if deepthink is not None:
            data["deepthink"] = deepthink
        if overdrive is not None:
            data["overdrive"] = overdrive
        if web_search is not None:
            data["web_search"] = web_search
        if eco is not None:
            data["eco"] = eco
        if temperature is not None:
            data["temperature"] = float(temperature)
        if iterations is not None:
            data["iterations"] = int(iterations)
        if regenerate_prompt is not None:
            data["regenerate_prompt"] = regenerate_prompt
        if edited_sequence is not None:
            data["edited_sequence"] = edited_sequence
        
        # Check if any settings are being updated
        if len(data) <= 1:  # Just the ID
            raise ValueError("At least one setting must be provided to update")
            
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
            
        return self._make_request("PUT", f"{self.sequence_url}/update", json_data=data)
    
    def get_sequence_history(
        self,
        sequence_id: str, 
        page: int = 1, 
        limit: int = 10,
        history_type: str = None, 
        include_current: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get history of changes for a sequence.
        
        Args:
            sequence_id: ID of the sequence
            page: Page number for pagination
            limit: Number of items per page
            history_type: Filter by history type ("update", "generation", "prompt", "media_change", or "selfupdate")
            include_current: Whether to include the current state
            
        Returns:
            Dictionary with history entries
            
        Raises:
            ValueError: If sequence_id is not provided or parameters are invalid
        """
        if not sequence_id:
            raise ValueError("sequence_id is required")
            
        # Validate history_type if provided
        if history_type and history_type not in ["update", "generation", "prompt", "media_change", "selfupdate"]:
            raise ValueError("history_type must be one of: 'update', 'generation', 'prompt', 'media_change', 'selfupdate'")
        
        # Validate pagination parameters
        if page < 1:
            raise ValueError("page must be at least 1")
        if limit < 1:
            raise ValueError("limit must be at least 1")
            
        params = {
            "sequence_id": sequence_id,
            "page": page,
            "limit": limit,
            "include_current": str(include_current).lower()
        }
        
        if history_type:
            params["history_type"] = history_type
            
        # Add any additional kwargs for backward compatibility
        params.update(kwargs)
            
        return self._make_request("GET", f"{self.sequence_url}/history", params=params)
    
    def get_sequence_media(
        self,
        sequence_id: str = None, 
        project_id: str = None,
        include_analysis: bool = False, 
        generate_thumbnail: bool = True,
        generate_streamable: bool = True, 
        generate_download: bool = False,
        **kwargs
    ) -> Dict:
        """
        Get media files used in a sequence.
        
        Args:
            sequence_id: ID of the sequence (either this or project_id must be provided)
            project_id: ID of the project (either this or sequence_id must be provided)
            include_analysis: Whether to include detailed analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            
        Returns:
            Dictionary with media files grouped by type (clips, audios, voiceover)
            
        Raises:
            ValueError: If neither sequence_id nor project_id is provided
            
        Notes:
            Set generate_download=True only when you need to download the original files.
            For preview purposes, use generate_streamable=True instead.
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
            
        params = {
            "include_analysis": str(include_analysis).lower(),
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if sequence_id:
            params["sequence_id"] = sequence_id
        if project_id:
            params["project_id"] = project_id
            
        # Add any additional kwargs for backward compatibility
        params.update(kwargs)
            
        return self._make_request("GET", f"{self.sequence_url}/media_involved", params=params)
    
    # Sequence Editing Operations
    
    def reorder_sequence_items(
        self,
        sequence_id: str, 
        array_type: str, 
        new_order: List[int],
        **kwargs
    ) -> Dict:
        """
        Reorder items in a sequence array.
        
        Args:
            sequence_id: ID of the sequence to modify
            array_type: Type of array to modify ("clips" or "audios")
            new_order: List of indices in the new order
            
        Returns:
            Dictionary with operation confirmation
            
        Raises:
            ValueError: If parameters are invalid or missing
            
        Example:
            # Swap first and second clips
            reorder_sequence_items(sequence_id="seq_123", array_type="clips", new_order=[1, 0, 2, 3])
        """
        if not sequence_id:
            raise ValueError("sequence_id is required")
            
        if array_type not in ['clips', 'audios']:
            raise ValueError("array_type must be either 'clips' or 'audios'")
            
        if not isinstance(new_order, list) or not all(isinstance(i, int) for i in new_order):
            raise ValueError("new_order must be a list of integers")
            
        data = {
            "sequence_id": sequence_id,
            "array_type": array_type,
            "new_order": new_order
        }
        
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
        
        return self._make_request("PUT", f"{self.sequence_url}/reorder", json_data=data)
    
    def edit_sequence_item(
        self,
        sequence_id: str, 
        item_type: str, 
        item_index: int = None, 
        updated_item: Dict = None,
        file_id: str = None,
        stock_id: str = None,
        **kwargs
    ) -> Dict:
        """
        Edit an item in a sequence.
        
        Args:
            sequence_id: ID of the sequence to modify
            item_type: Type of item to edit ("clips", "audios", or "voiceover")
            item_index: Index of the item to update (required for clips and audios)
            updated_item: Updated item data
            file_id: Optional file ID to replace the media (alternative to providing in updated_item)
            stock_id: Optional stock media ID to replace the media
            
        Returns:
            Dictionary with operation confirmation
            
        Raises:
            ValueError: If parameters are invalid or missing
        """
        if not sequence_id:
            raise ValueError("sequence_id is required")
            
        if item_type not in ['clips', 'audios', 'voiceover']:
            raise ValueError("item_type must be one of: 'clips', 'audios', 'voiceover'")
            
        if item_type != 'voiceover' and item_index is None:
            raise ValueError(f"item_index is required for item_type '{item_type}'")
            
        if not updated_item and not (file_id or stock_id):
            raise ValueError("Either updated_item, file_id, or stock_id must be provided")
            
        data = {
            "sequence_id": sequence_id,
            "item_type": item_type
        }
        
        if item_index is not None:
            data["item_index"] = item_index
            
        if updated_item:
            data["updated_item"] = updated_item
            
        if file_id:
            data["file_id"] = file_id
            
        if stock_id:
            data["stock_id"] = stock_id
        
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
            
        return self._make_request("PUT", f"{self.sequence_url}/edit/item", json_data=data)
    
    def change_sequence_media(
        self,
        sequence_id: str, 
        item_type: str, 
        item_index: int = None,
        file_id: str = None, 
        stock_id: str = None, 
        path: str = None,
        **kwargs
    ) -> Dict:
        """
        Change media for an item in a sequence.
        
        Args:
            sequence_id: ID of the sequence to modify
            item_type: Type of item to modify ("clips", "audios", or "voiceover")
            item_index: Index of the item to update (required for clips and audios)
            file_id: ID of the file to use (one of file_id, stock_id, or path must be provided)
            stock_id: ID of the stock media to use (one of file_id, stock_id, or path must be provided)
            path: Direct path to the media file (one of file_id, stock_id, or path must be provided)
            
        Returns:
            Dictionary with operation confirmation
            
        Raises:
            ValueError: If parameters are invalid or missing
            
        Notes:
            Use this method for simple media replacement. For more complex changes,
            use edit_sequence_item() instead.
        """
        if not sequence_id:
            raise ValueError("sequence_id is required")
            
        if item_type not in ['clips', 'audios', 'voiceover']:
            raise ValueError("item_type must be one of: 'clips', 'audios', 'voiceover'")
            
        if item_type != 'voiceover' and item_index is None:
            raise ValueError(f"item_index is required for item_type '{item_type}'")
            
        if not any([file_id, stock_id, path]):
            raise ValueError("One of file_id, stock_id, or path must be provided")
            
        data = {
            "sequence_id": sequence_id,
            "item_type": item_type
        }
        
        if item_index is not None:
            data["item_index"] = item_index
            
        if file_id:
            data["file_id"] = file_id
        elif stock_id:
            data["stock_id"] = stock_id
        elif path:
            data["path"] = path
        
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
            
        return self._make_request("PUT", f"{self.sequence_url}/change_media", json_data=data)
        
    # Convenience methods and workflows
    
    def update_and_regenerate(
        self,
        sequence_id: str = None,
        project_id: str = None,
        regenerate_prompt: str = None,
        include_history: bool = True,
        wait_for_completion: bool = False,
        check_interval: int = 5,
        timeout: int = 600
    ) -> Dict:
        """
        Update a sequence with latest data and then regenerate it in one operation.
        This is a convenience method that combines update_sequence() and redo_sequence().
        
        Args:
            sequence_id: ID of the sequence (either this or project_id must be provided)
            project_id: ID of the project (either this or sequence_id must be provided)
            regenerate_prompt: Optional prompt to guide the regeneration
            include_history: Whether to include sequence history as context
            wait_for_completion: Whether to wait for job completion
            check_interval: Seconds between job status checks (if waiting)
            timeout: Maximum seconds to wait (if waiting)
            
        Returns:
            Dictionary with the regeneration job details
            
        Raises:
            ValueError: If parameters are invalid
            TimeoutError: If job doesn't complete within the timeout period
            
        Notes:
            This is particularly useful when upstream components (storyboard or voiceover)
            have been modified and you want to regenerate the sequence with those changes.
        """
        if not sequence_id and not project_id:
            raise ValueError("Either sequence_id or project_id must be provided")
            
        # First update the sequence with latest data
        update_result = self.update_sequence(
            sequence_id=sequence_id,
            project_id=project_id,
            update_ai_params=True
        )
        
        # Then regenerate the sequence
        redo_result = self.redo_sequence(
            sequence_id=sequence_id if sequence_id else update_result.get('sequence_id'),
            project_id=project_id,
            include_history=include_history,
            regenerate_prompt=regenerate_prompt
        )
        
        if wait_for_completion:
            # TODO: Implement job status checking until completion or timeout
            # This would likely need a get_job_status method and polling logic
            pass
            
        return redo_result
    
    def swap_media(
        self, 
        sequence_id: str,
        first_item_index: int,
        second_item_index: int,
        array_type: str = "clips"
    ) -> Dict:
        """
        Swap two media items in a sequence.
        
        Args:
            sequence_id: ID of the sequence to modify
            first_item_index: Index of the first item
            second_item_index: Index of the second item
            array_type: Type of array to modify ("clips" or "audios")
            
        Returns:
            Dictionary with operation confirmation
            
        Raises:
            ValueError: If parameters are invalid
            
        Notes:
            This is a convenience method that uses reorder_sequence_items() under the hood.
        """
        if not sequence_id:
            raise ValueError("sequence_id is required")
            
        if array_type not in ["clips", "audios"]:
            raise ValueError("array_type must be either 'clips' or 'audios'")
            
        # Get the sequence to determine the array length
        sequence = self.get_sequence(sequence_id=sequence_id)
        
        # Get edited_sequence if available, otherwise use job results
        sequence_data = None
        if sequence.get('edited_sequence'):
            sequence_data = sequence.get('edited_sequence')
        elif sequence.get('old_job_result'):
            sequence_data = sequence.get('old_job_result').get('results')
        
        if not sequence_data:
            raise ValueError("No sequence data available")
            
        # Get the array to work with
        items_array = sequence_data.get(array_type, [])
        if not items_array:
            raise ValueError(f"No {array_type} found in the sequence")
            
        # Validate indices
        array_length = len(items_array)
        if not (0 <= first_item_index < array_length and 0 <= second_item_index < array_length):
            raise ValueError(f"Indices must be between 0 and {array_length-1}")
            
        # Create the new order
        new_order = list(range(array_length))
        new_order[first_item_index], new_order[second_item_index] = new_order[second_item_index], new_order[first_item_index]
        
        # Reorder the items
        return self.reorder_sequence_items(
            sequence_id=sequence_id,
            array_type=array_type,
            new_order=new_order
        )
