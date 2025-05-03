import os
import json
import requests
import uuid
import mimetypes
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from .base_client import BaseClient

class PromptClient(BaseClient):
    """
    Client for interacting with Storylinez Prompt API.
    Provides methods for managing prompts, reference videos, and content search operations.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the PromptClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.prompts_url = f"{self.base_url}/prompts"
        
        # Define allowed media formats
        self.allowed_formats = {
            'VIDEO': ['mp4'],
            'AUDIO': ['mp3', 'wav'], 
            'IMAGE': ['jpg', 'jpeg', 'png']
        }
        
        # Specifically for reference videos, only mp4 is supported
        self.allowed_video_formats = self.allowed_formats['VIDEO']
    
    # Helper method to validate file extensions
    def _validate_file_extension(self, filename: str, media_type: str) -> str:
        """
        Validates that a file has an allowed extension for its media type.
        
        Args:
            filename: The filename to check
            media_type: Type of media ('VIDEO', 'AUDIO', or 'IMAGE')
            
        Returns:
            The file extension without the dot
            
        Raises:
            ValueError: If the file extension is not allowed for the media type
        """
        if media_type not in self.allowed_formats:
            raise ValueError(f"Unknown media type: {media_type}")
            
        extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if not extension:
            raise ValueError(f"Filename '{filename}' has no extension. Valid {media_type.lower()} extensions are: {', '.join(self.allowed_formats[media_type])}")
            
        if extension not in self.allowed_formats[media_type]:
            raise ValueError(f"File extension '{extension}' is not supported. Valid {media_type.lower()} extensions are: {', '.join(self.allowed_formats[media_type])}")
            
        return extension
    
    # Prompt Operations
    
    def create_text_prompt(self, 
                         project_id: str, 
                         main_prompt: str, 
                         document_context: Union[str, List[str]] = "",
                         temperature: float = 0.7, 
                         total_length: int = 20, 
                         iterations: int = 1,
                         deepthink: bool = False, 
                         overdrive: bool = False, 
                         web_search: bool = False,
                         eco: bool = False, 
                         skip_voiceover: bool = False,
                         voiceover_mode: str = "generated") -> Dict:
        """
        Create a new text-based prompt for a project.
        
        Args:
            project_id: ID of the project to create the prompt for
            main_prompt: The actual prompt text
            document_context: Optional document context to support the prompt
            temperature: AI temperature parameter (0.0-1.0)
            total_length: Target length of the video in seconds (10-60)
            iterations: Number of refinement iterations (1-10)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            skip_voiceover: Whether to skip generating voiceover
            voiceover_mode: Voiceover mode ('generated' or 'uploaded')
            
        Returns:
            Dictionary with the created prompt details
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Input validations
        if not project_id:
            raise ValueError("project_id is required")
            
        if not main_prompt or not main_prompt.strip():
            raise ValueError("main_prompt is required and cannot be empty")
            
        # Normalize temperature value
        try:
            temperature = float(temperature)
        except (TypeError, ValueError):
            raise ValueError(f"temperature must be a number between 0 and 1, got: {temperature}")
            
        if temperature < 0 or temperature > 1:
            raise ValueError(f"temperature must be between 0 and 1, got: {temperature}")
            
        # Normalize total_length
        try:
            total_length = int(total_length)
        except (TypeError, ValueError):
            raise ValueError(f"total_length must be an integer between 10 and 60, got: {total_length}")
            
        if total_length < 10 or total_length > 60:
            raise ValueError(f"total_length must be between 10 and 60 seconds, got: {total_length}")
            
        # Normalize iterations
        try:
            iterations = int(iterations)
        except (TypeError, ValueError):
            raise ValueError(f"iterations must be an integer between 1 and 10, got: {iterations}")
            
        if iterations < 1 or iterations > 10:
            raise ValueError(f"iterations must be between 1 and 10, got: {iterations}")
            
        # Validate voiceover_mode
        if voiceover_mode not in ["generated", "uploaded"]:
            raise ValueError(f"voiceover_mode must be either 'generated' or 'uploaded', got: {voiceover_mode}")
        
        # Ensure document_context is always a list of strings
        if isinstance(document_context, str):
            document_context = [document_context]
        elif not isinstance(document_context, list):
            document_context = []
        
        data = {
            "project_id": project_id,
            "main_prompt": main_prompt,
            "document_context": document_context,
            "temperature": temperature,
            "total_length": total_length,
            "iterations": iterations,
            "deepthink": bool(deepthink),
            "overdrive": bool(overdrive),
            "web_search": bool(web_search),
            "eco": bool(eco),
            "skip_voiceover": bool(skip_voiceover),
            "voiceover_mode": voiceover_mode
        }
        
        return self._make_request("POST", f"{self.prompts_url}/create", json_data=data)
    
    def create_video_prompt(self, 
                          project_id: str, 
                          reference_video_id: str,
                          temperature: float = 0.7, 
                          total_length: int = 20, 
                          iterations: int = 1,
                          deepthink: bool = False, 
                          overdrive: bool = False, 
                          web_search: bool = False,
                          eco: bool = False, 
                          skip_voiceover: bool = False,
                          voiceover_mode: str = "generated", 
                          include_detailed_analysis: bool = False) -> Dict:
        """
        Create a new video-based prompt for a project.
        
        Args:
            project_id: ID of the project to create the prompt for
            reference_video_id: ID of the reference video to use
            temperature: AI temperature parameter (0.0-1.0)
            total_length: Target length of the video in seconds (10-60)
            iterations: Number of refinement iterations (1-10)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            skip_voiceover: Whether to skip generating voiceover
            voiceover_mode: Voiceover mode ('generated' or 'uploaded')
            include_detailed_analysis: Whether to include detailed video analysis in the prompt
            
        Returns:
            Dictionary with the created prompt details
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Input validations
        if not project_id:
            raise ValueError("project_id is required")
            
        if not reference_video_id:
            raise ValueError("reference_video_id is required")
            
        # Normalize temperature value
        try:
            temperature = float(temperature)
        except (TypeError, ValueError):
            raise ValueError(f"temperature must be a number between 0 and 1, got: {temperature}")
            
        if temperature < 0 or temperature > 1:
            raise ValueError(f"temperature must be between 0 and 1, got: {temperature}")
            
        # Normalize total_length
        try:
            total_length = int(total_length)
        except (TypeError, ValueError):
            raise ValueError(f"total_length must be an integer between 10 and 60, got: {total_length}")
            
        if total_length < 10 or total_length > 60:
            raise ValueError(f"total_length must be between 10 and 60 seconds, got: {total_length}")
            
        # Normalize iterations
        try:
            iterations = int(iterations)
        except (TypeError, ValueError):
            raise ValueError(f"iterations must be an integer between 1 and 10, got: {iterations}")
            
        if iterations < 1 or iterations > 10:
            raise ValueError(f"iterations must be between 1 and 10, got: {iterations}")
            
        # Validate voiceover_mode
        if voiceover_mode not in ["generated", "uploaded"]:
            raise ValueError(f"voiceover_mode must be either 'generated' or 'uploaded', got: {voiceover_mode}")
        
        data = {
            "project_id": project_id,
            "reference_video_id": reference_video_id,
            "temperature": temperature,
            "total_length": total_length,
            "iterations": iterations,
            "deepthink": bool(deepthink),
            "overdrive": bool(overdrive),
            "web_search": bool(web_search),
            "eco": bool(eco),
            "skip_voiceover": bool(skip_voiceover),
            "voiceover_mode": voiceover_mode,
            "include_detailed_analysis": bool(include_detailed_analysis)
        }
        
        return self._make_request("POST", f"{self.prompts_url}/create", json_data=data)
    
    def create_prompt(self, project_id: str, **kwargs) -> Dict:
        """
        Create a prompt for a project - automatically determines whether to create a text or video prompt.
        
        Args:
            project_id: ID of the project to create the prompt for
            **kwargs: Either provide 'main_prompt' for text prompts or 'reference_video_id' for video prompts,
                     along with other optional parameters
            
        Returns:
            Dictionary with the created prompt details
            
        Raises:
            ValueError: If unable to determine prompt type or if parameters are invalid
        """
        if "main_prompt" in kwargs:
            # Creating a text prompt
            return self.create_text_prompt(project_id=project_id, **kwargs)
        elif "reference_video_id" in kwargs:
            # Creating a video prompt
            return self.create_video_prompt(project_id=project_id, **kwargs)
        else:
            raise ValueError("Either main_prompt (for text prompts) or reference_video_id (for video prompts) must be provided")
    
    def get_prompt(self, prompt_id: str = None, project_id: str = None) -> Dict:
        """
        Get a prompt by ID or project ID.
        
        Args:
            prompt_id: ID of the prompt to retrieve (either this or project_id must be provided)
            project_id: ID of the project to retrieve the prompt for (either this or prompt_id must be provided)
            
        Returns:
            Dictionary with the prompt details
            
        Raises:
            ValueError: If neither prompt_id nor project_id is provided
        """
        if not prompt_id and not project_id:
            raise ValueError("Either prompt_id or project_id must be provided")
            
        params = {}
        if prompt_id:
            params["prompt_id"] = prompt_id
        if project_id:
            params["project_id"] = project_id
            
        return self._make_request("GET", f"{self.prompts_url}/get", params=params)
    
    def get_prompt_by_project(self, project_id: str) -> Dict:
        """
        Get a prompt for a specific project.
        
        Args:
            project_id: ID of the project to retrieve the prompt for
            
        Returns:
            Dictionary with the prompt details
            
        Raises:
            ValueError: If project_id is not provided
        """
        if not project_id:
            raise ValueError("project_id is required")
            
        params = {"project_id": project_id}
        return self._make_request("GET", f"{self.prompts_url}/get_by_project", params=params)
    
    def update_prompt(self, 
                     prompt_id: str = None, 
                     project_id: str = None, 
                     temperature: float = None,
                     total_length: int = None,
                     iterations: int = None,
                     deepthink: bool = None,
                     overdrive: bool = None,
                     web_search: bool = None,
                     eco: bool = None,
                     main_prompt: str = None,
                     document_context: Union[str, List[str]] = None,
                     reference_video_id: str = None,
                     skip_voiceover: bool = None,
                     voiceover_mode: str = None) -> Dict:
        """
        Update an existing prompt.
        
        Args:
            prompt_id: ID of the prompt to update (either this or project_id must be provided)
            project_id: ID of the project whose prompt to update (either this or prompt_id must be provided)
            temperature: AI temperature parameter (0.0-1.0)
            total_length: Target length of the video in seconds (10-60)
            iterations: Number of refinement iterations (1-10)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            main_prompt: New text for text-based prompts
            document_context: New document context for text-based prompts
            reference_video_id: New reference video ID for video-based prompts
            skip_voiceover: Whether to skip generating voiceover
            voiceover_mode: Voiceover mode ('generated' or 'uploaded')
            
        Returns:
            Dictionary with update confirmation
            
        Raises:
            ValueError: If parameters are invalid or no update parameters are provided
        """
        if not prompt_id and not project_id:
            raise ValueError("Either prompt_id or project_id must be provided")
            
        params = {}
        if prompt_id:
            params["prompt_id"] = prompt_id
        if project_id:
            params["project_id"] = project_id
        
        # Build update data with only provided values
        update_data = {}
        
        # Validation and assignment for each parameter
        if temperature is not None:
            try:
                temperature = float(temperature)
            except (TypeError, ValueError):
                raise ValueError(f"temperature must be a number between 0 and 1, got: {temperature}")
                
            if temperature < 0 or temperature > 1:
                raise ValueError(f"temperature must be between 0 and 1, got: {temperature}")
                
            update_data['temperature'] = temperature
            
        if total_length is not None:
            try:
                total_length = int(total_length)
            except (TypeError, ValueError):
                raise ValueError(f"total_length must be an integer between 10 and 60, got: {total_length}")
                
            if total_length < 10 or total_length > 60:
                raise ValueError(f"total_length must be between 10 and 60 seconds, got: {total_length}")
                
            update_data['total_length'] = total_length
            
        if iterations is not None:
            try:
                iterations = int(iterations)
            except (TypeError, ValueError):
                raise ValueError(f"iterations must be an integer between 1 and 10, got: {iterations}")
                
            if iterations < 1 or iterations > 10:
                raise ValueError(f"iterations must be between 1 and 10, got: {iterations}")
                
            update_data['iterations'] = iterations
            
        # Boolean flags
        if deepthink is not None:
            update_data['deepthink'] = bool(deepthink)
            
        if overdrive is not None:
            update_data['overdrive'] = bool(overdrive)
            
        if web_search is not None:
            update_data['web_search'] = bool(web_search)
            
        if eco is not None:
            update_data['eco'] = bool(eco)
            
        if skip_voiceover is not None:
            update_data['skip_voiceover'] = bool(skip_voiceover)
            
        # Text fields
        if main_prompt is not None:
            if not main_prompt.strip():
                raise ValueError("main_prompt cannot be empty if provided")
            update_data['main_prompt'] = main_prompt
            
        if document_context is not None:
            # Ensure document_context is always a list of strings
            if isinstance(document_context, str):
                update_data['document_context'] = [document_context]
            elif isinstance(document_context, list):
                update_data['document_context'] = document_context
            else:
                update_data['document_context'] = []
            
        if reference_video_id is not None:
            if not reference_video_id.strip():
                raise ValueError("reference_video_id cannot be empty if provided")
            update_data['reference_video_id'] = reference_video_id
            
        # Voiceover mode
        if voiceover_mode is not None:
            if voiceover_mode not in ['generated', 'uploaded']:
                raise ValueError(f"voiceover_mode must be either 'generated' or 'uploaded', got: {voiceover_mode}")
            update_data['voiceover_mode'] = voiceover_mode
            
        if not update_data:
            raise ValueError("At least one field to update must be provided")
            
        return self._make_request("PUT", f"{self.prompts_url}/update", params=params, json_data=update_data)
    
    def switch_to_text_prompt(self, prompt_id: str, main_prompt: str, document_context: Union[str, List[str]] = "") -> Dict:
        """
        Switch a prompt to text type.
        
        Args:
            prompt_id: ID of the prompt to switch
            main_prompt: The main text prompt
            document_context: Optional document context
            
        Returns:
            Dictionary with the updated prompt details
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not prompt_id:
            raise ValueError("prompt_id is required")
            
        if not main_prompt or not main_prompt.strip():
            raise ValueError("main_prompt is required and cannot be empty")
            
        # Ensure document_context is always a list of strings
        if isinstance(document_context, str):
            document_context = [document_context]
        elif not isinstance(document_context, list):
            document_context = []
        
        data = {
            "main_prompt": main_prompt,
            "document_context": document_context
        }
            
        params = {"prompt_id": prompt_id}
        return self._make_request("PUT", f"{self.prompts_url}/switch_type", params=params, json_data=data)
    
    def switch_to_video_prompt(self, prompt_id: str, reference_video_id: str, include_detailed_analysis: bool = False) -> Dict:
        """
        Switch a prompt to video type.
        
        Args:
            prompt_id: ID of the prompt to switch
            reference_video_id: ID of the reference video to use
            include_detailed_analysis: Whether to include detailed analysis of the video
            
        Returns:
            Dictionary with the updated prompt details
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not prompt_id:
            raise ValueError("prompt_id is required")
            
        if not reference_video_id or not reference_video_id.strip():
            raise ValueError("reference_video_id is required and cannot be empty")
            
        data = {
            "reference_video_id": reference_video_id,
            "include_detailed_analysis": bool(include_detailed_analysis)
        }
            
        params = {"prompt_id": prompt_id}
        return self._make_request("PUT", f"{self.prompts_url}/switch_type", params=params, json_data=data)
    
    def switch_prompt_type(self, prompt_id: str, **kwargs) -> Dict:
        """
        Switch between text and video prompt types.
        
        Args:
            prompt_id: ID of the prompt to switch
            **kwargs: For switching to text prompt: main_prompt and document_context (optional)
                     For switching to video prompt: reference_video_id and include_detailed_analysis (optional)
            
        Returns:
            Dictionary with the updated prompt details
            
        Raises:
            ValueError: If parameters are invalid or prompt type cannot be determined
        """
        if "main_prompt" in kwargs:
            # Switching to text prompt
            document_context = kwargs.get("document_context", "")
            # Ensure document_context is always a list of strings
            if isinstance(document_context, str):
                document_context = [document_context]
            elif not isinstance(document_context, list):
                document_context = []
            return self.switch_to_text_prompt(
                prompt_id=prompt_id,
                main_prompt=kwargs["main_prompt"],
                document_context=document_context
            )
        elif "reference_video_id" in kwargs:
            # Switching to video prompt
            return self.switch_to_video_prompt(
                prompt_id=prompt_id,
                reference_video_id=kwargs["reference_video_id"],
                include_detailed_analysis=kwargs.get("include_detailed_analysis", False)
            )
        else:
            raise ValueError("Either main_prompt (for text prompts) or reference_video_id (for video prompts) must be provided")
    
    # Reference Video Operations
    
    def get_reference_video_upload_link(self, filename: str, org_id: str = None, file_size: int = 0) -> Dict:
        """
        Generate an upload link for a reference video.
        
        Args:
            filename: Name of the video file to upload (must be MP4 format)
            org_id: Organization ID (uses default if not provided)
            file_size: Size of the file in bytes (for storage quota check)
            
        Returns:
            Dictionary with upload URL and details
            
        Raises:
            ValueError: If parameters are invalid or file extension is not MP4 (only MP4 files are supported)
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not filename or not filename.strip():
            raise ValueError("filename is required and cannot be empty")
            
        # Check file extension - only mp4 is allowed for reference videos
        extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if extension != 'mp4':
            raise ValueError(f"For reference videos, only MP4 format is supported. Got '{extension}' instead.")
        
        self._validate_file_extension(filename, 'VIDEO')
        
        # Validate file size
        if file_size is not None:
            try:
                file_size = int(file_size)
                if file_size < 0:
                    raise ValueError("file_size cannot be negative")
            except (TypeError, ValueError):
                raise ValueError(f"file_size must be a positive integer, got: {file_size}")
        
        params = {
            "org_id": org_id,
            "filename": filename,
            "file_size": file_size
        }
        
        return self._make_request("GET", f"{self.prompts_url}/upload/create_link", params=params)
    
    def complete_reference_video_upload(self, 
                                      upload_id: str = None, 
                                      key: str = None, 
                                      org_id: str = None, 
                                      filename: str = None,
                                      mimetype: str = None,
                                      context: str = "", 
                                      tags: List[str] = None,
                                      company_details: str = "",
                                      analyze_audio: bool = True) -> Dict:
        """
        Complete a reference video upload.
        
        Args:
            upload_id: ID of the upload (either this or key must be provided)
            key: S3 key of the uploaded file (either this or upload_id must be provided)
            org_id: Organization ID (uses default if not provided)
            filename: Name to use for the file (defaults to the uploaded filename)
            mimetype: MIME type of the video (defaults to video/mp4)
            context: Context description for the video
            tags: List of tags for the video
            company_details: Company details for contextual analysis
            analyze_audio: Whether to analyze audio in the video
            
        Returns:
            Dictionary with the registered video details
            
        Raises:
            ValueError: If required parameters are missing
                       Note: Only MP4 files are supported for reference videos
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not upload_id and not key:
            raise ValueError("Either upload_id or key must be provided")
            
        # Normalize tags
        if tags is None:
            tags = []
        elif not isinstance(tags, list):
            tags = [str(tags)]
        
        # Determine mimetype based on file extension if not provided
        if mimetype is None and filename:
            guessed_type = mimetypes.guess_type(filename)[0]
            if guessed_type and guessed_type.startswith('video/'):
                mimetype = guessed_type
            else:
                mimetype = 'video/mp4'  # Default
        elif mimetype is None:
            mimetype = 'video/mp4'
            
        # Ensure mimetype is video
        if not mimetype.startswith('video/'):
            raise ValueError(f"MIME type '{mimetype}' is not a valid video type")
            
        data = {
            "org_id": org_id,
            "context": context or "",
            "tags": tags,
            "company_details": company_details or "",
            "analyze_audio": bool(analyze_audio)
        }
        
        if upload_id:
            data["upload_id"] = upload_id
        if key:
            data["key"] = key
        if filename:
            data["filename"] = filename
        if mimetype:
            data["mimetype"] = mimetype
            
        return self._make_request("POST", f"{self.prompts_url}/upload/complete", json_data=data)
    
    def list_reference_videos(self, 
                            org_id: str = None, 
                            detailed: bool = False, 
                            generate_thumbnail: bool = True, 
                            generate_streamable: bool = False,
                            generate_download: bool = False, 
                            include_usage: bool = False,
                            max_prompts_per_video: int = 5, 
                            page: int = 1, 
                            limit: int = 10) -> Dict:
        """
        List all reference videos for an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            detailed: Whether to include detailed analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            include_usage: Whether to include usage information
            max_prompts_per_video: Maximum number of prompts to return per video if include_usage is True
            page: Page number for pagination (starting from 1)
            limit: Number of items per page (max 50)
            
        Returns:
            Dictionary with list of reference videos and pagination metadata
            
        Raises:
            ValueError: If org_id is not provided or pagination parameters are invalid
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Normalize pagination parameters
        try:
            page = int(page)
        except (TypeError, ValueError):
            raise ValueError(f"page must be a positive integer, got: {page}")
            
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValueError(f"limit must be a positive integer, got: {limit}")
            
        if page < 1:
            raise ValueError(f"page must be at least 1, got: {page}")
            
        if limit < 1:
            raise ValueError(f"limit must be at least 1, got: {limit}")
            
        if limit > 50:
            limit = 50
            
        # Normalize max_prompts_per_video
        try:
            max_prompts_per_video = int(max_prompts_per_video)
        except (TypeError, ValueError):
            max_prompts_per_video = 5
            
        if max_prompts_per_video < 1:
            max_prompts_per_video = 1
        
        params = {
            "org_id": org_id,
            "detailed": str(bool(detailed)).lower(),
            "generate_thumbnail": str(bool(generate_thumbnail)).lower(),
            "generate_streamable": str(bool(generate_streamable)).lower(),
            "generate_download": str(bool(generate_download)).lower(),
            "include_usage": str(bool(include_usage)).lower(),
            "max_prompts_per_video": max_prompts_per_video,
            "page": page,
            "limit": limit
        }
        
        return self._make_request("GET", f"{self.prompts_url}/reference-videos/list", params=params)
    
    def get_reference_video_details(self, 
                                 file_id: str, 
                                 detailed: bool = True,
                                 generate_thumbnail: bool = True, 
                                 generate_streamable: bool = True,
                                 generate_download: bool = True, 
                                 include_usage: bool = True) -> Dict:
        """
        Get details of a specific reference video.
        
        Args:
            file_id: ID of the reference video
            detailed: Whether to include detailed analysis data
            generate_thumbnail: Whether to generate thumbnail URL
            generate_streamable: Whether to generate streamable URL
            generate_download: Whether to generate download URL
            include_usage: Whether to include usage information
            
        Returns:
            Dictionary with reference video details
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id or not file_id.strip():
            raise ValueError("file_id is required and cannot be empty")
            
        params = {
            "file_id": file_id,
            "detailed": str(bool(detailed)).lower(),
            "generate_thumbnail": str(bool(generate_thumbnail)).lower(),
            "generate_streamable": str(bool(generate_streamable)).lower(),
            "generate_download": str(bool(generate_download)).lower(),
            "include_usage": str(bool(include_usage)).lower()
        }
        
        return self._make_request("GET", f"{self.prompts_url}/reference-videos/details", params=params)
    
    def search_reference_videos(self, 
                             query: str, 
                             org_id: str = None, 
                             page: int = 1,
                             limit: int = 10, 
                             detailed: bool = False, 
                             generate_thumbnail: bool = True, 
                             generate_streamable: bool = False,
                             generate_download: bool = False, 
                             include_usage: bool = False,
                             max_prompts_per_video: int = 5) -> Dict:
        """
        Search for reference videos by filename.
        
        Args:
            query: Search term
            org_id: Organization ID (uses default if not provided)
            page: Page number for pagination
            limit: Number of items per page
            detailed: Whether to include detailed analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            include_usage: Whether to include usage information
            max_prompts_per_video: Maximum number of prompts to return per video if include_usage is True
            
        Returns:
            Dictionary with search results
            
        Raises:
            ValueError: If query is empty or org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not query or not query.strip():
            raise ValueError("query is required and cannot be empty")
            
        # Normalize pagination parameters
        try:
            page = int(page)
        except (TypeError, ValueError):
            raise ValueError(f"page must be a positive integer, got: {page}")
            
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValueError(f"limit must be a positive integer, got: {limit}")
            
        if page < 1:
            raise ValueError(f"page must be at least 1, got: {page}")
            
        if limit < 1:
            raise ValueError(f"limit must be at least 1, got: {limit}")
            
        if limit > 50:
            limit = 50
            
        # Normalize max_prompts_per_video
        try:
            max_prompts_per_video = int(max_prompts_per_video)
        except (TypeError, ValueError):
            max_prompts_per_video = 5
            
        if max_prompts_per_video < 1:
            max_prompts_per_video = 1
        
        params = {
            "org_id": org_id,
            "query": query.strip(),
            "page": page,
            "limit": limit,
            "detailed": str(bool(detailed)).lower(),
            "generate_thumbnail": str(bool(generate_thumbnail)).lower(),
            "generate_streamable": str(bool(generate_streamable)).lower(),
            "generate_download": str(bool(generate_download)).lower(),
            "include_usage": str(bool(include_usage)).lower(),
            "max_prompts_per_video": max_prompts_per_video
        }
        
        return self._make_request("GET", f"{self.prompts_url}/reference-videos/search", params=params)
    
    def delete_reference_video(self, file_id: str) -> Dict:
        """
        Delete a reference video.
        
        Args:
            file_id: ID of the reference video to delete
            
        Returns:
            Dictionary with deletion confirmation
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id or not file_id.strip():
            raise ValueError("file_id is required and cannot be empty")
            
        params = {"file_id": file_id}
        return self._make_request("DELETE", f"{self.prompts_url}/reference-videos/delete", params=params)
    
    def get_reference_videos_by_ids(self, 
                                  file_ids: List[str], 
                                  org_id: str = None,
                                  detailed: bool = False, 
                                  generate_thumbnail: bool = True,
                                  generate_streamable: bool = False, 
                                  generate_download: bool = False,
                                  include_usage: bool = False) -> Dict:
        """
        Get multiple reference videos by their IDs.
        
        Args:
            file_ids: List of reference video IDs
            org_id: Organization ID (uses default if not provided)
            detailed: Whether to include detailed analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            include_usage: Whether to include usage information
            
        Returns:
            Dictionary with requested reference videos
            
        Raises:
            ValueError: If file_ids is empty or org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not file_ids:
            raise ValueError("file_ids list cannot be empty")
            
        if not isinstance(file_ids, list):
            raise ValueError("file_ids must be a list")
            
        if len(file_ids) > 50:
            raise ValueError("Cannot request more than 50 reference videos at once")
            
        # Remove empty values
        file_ids = [fid for fid in file_ids if fid]
        if not file_ids:
            raise ValueError("file_ids list cannot contain only empty values")
            
        params = {
            "org_id": org_id,
            "detailed": str(bool(detailed)).lower(),
            "generate_thumbnail": str(bool(generate_thumbnail)).lower(),
            "generate_streamable": str(bool(generate_streamable)).lower(),
            "generate_download": str(bool(generate_download)).lower(),
            "include_usage": str(bool(include_usage)).lower()
        }
        
        data = {"file_ids": file_ids}
        
        return self._make_request("POST", f"{self.prompts_url}/reference-videos/get_by_ids", params=params, json_data=data)
    
    def _validate_video_file(self, file_path: str) -> Tuple[str, int]:
        """
        Validates a video file and returns its name and size.
        For reference videos, only MP4 format is supported.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Tuple of (filename, file_size)
            
        Raises:
            ValueError: If file doesn't exist or is not a valid MP4 video
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
            
        # Validate file extension - only mp4 is supported
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1].lower().lstrip('.')
        
        if extension != 'mp4':
            raise ValueError(f"Only MP4 format is supported for reference videos. Got '{extension}' instead.")
            
        self._validate_file_extension(filename, 'VIDEO')
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return filename, file_size
    
    def upload_reference_video(self, 
                             file_path: str, 
                             org_id: str = None, 
                             context: str = "", 
                             tags: List[str] = None, 
                             company_details: str = "",
                             analyze_audio: bool = True) -> Dict:
        """
        Upload a reference video file.
        This is a convenience method that handles both the link generation, upload, and registration.
        
        Args:
            file_path: Path to the video file on local disk (must be MP4 format)
            org_id: Organization ID (uses default if not provided)
            context: Context description for the video
            tags: List of tags for the video
            company_details: Company details for contextual analysis
            analyze_audio: Whether to analyze audio in the video
            
        Returns:
            Dictionary with the registered video details
            
        Raises:
            ValueError: If file is invalid or org_id is not provided
            FileNotFoundError: If file doesn't exist
            Note: Only MP4 files are supported for reference videos
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Validate file
        filename, file_size = self._validate_video_file(file_path)
        
        # Get MIME type
        mimetype = mimetypes.guess_type(file_path)[0] or 'video/mp4'
        
        # Generate upload link
        upload_info = self.get_reference_video_upload_link(
            filename=filename,
            org_id=org_id,
            file_size=file_size
        )
        
        # Check for errors in response
        if "error" in upload_info:
            raise ValueError(f"Error getting upload link: {upload_info.get('error')}")
        
        # Upload the file to the pre-signed URL
        upload_link = upload_info.get("upload_link")
        upload_id = upload_info.get("upload_id")
        
        if not upload_link:
            raise ValueError("Failed to get upload link from server")
            
        # Use requests to upload the file
        with open(file_path, 'rb') as file_data:
            upload_response = requests.put(upload_link, data=file_data)
            
            if upload_response.status_code >= 400:
                raise Exception(f"Reference video upload failed with status {upload_response.status_code}: {upload_response.text}")
        
        # Complete the upload and register the video
        return self.complete_reference_video_upload(
            upload_id=upload_id,
            org_id=org_id,
            filename=filename,
            mimetype=mimetype,
            context=context,
            tags=tags,
            company_details=company_details,
            analyze_audio=analyze_audio
        )
    
    def batch_upload_reference_videos(self, 
                                    file_paths: List[str], 
                                    org_id: str = None, 
                                    context: str = "", 
                                    tags: List[str] = None,
                                    analyze_audio: bool = True) -> List[Dict]:
        """
        Upload multiple reference video files in sequence.
        
        Args:
            file_paths: List of paths to video files (must all be MP4 format)
            org_id: Organization ID (uses default if not provided)
            context: Common context description for all videos
            tags: List of tags for all videos
            analyze_audio: Whether to analyze audio in the videos
            
        Returns:
            List of dictionaries with results for each upload
            
        Raises:
            ValueError: If file_paths is empty or org_id is not provided
            Note: Only MP4 files are supported for reference videos
        """
        if not file_paths:
            raise ValueError("file_paths list cannot be empty")
            
        results = []
        
        for file_path in file_paths:
            try:
                result = self.upload_reference_video(
                    file_path=file_path,
                    org_id=org_id,
                    context=context,
                    tags=tags,
                    analyze_audio=analyze_audio
                )
                results.append({
                    "file_path": file_path,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "file_path": file_path,
                    "success": False,
                    "error": str(e)
                })
                
        return results
    
    # Content Search Operations
    
    def generate_search_query(self, 
                      prompt_id: str = None, 
                      project_id: str = None, 
                      num_videos: int = 5, 
                      num_audio: int = 1, 
                      num_images: int = 0,
                      company_details: str = "", 
                      documents: List[str] = None,
                      temperature: float = None) -> Dict:
        """
        Start a search job to find content matching a prompt.
        
        Args:
            prompt_id: ID of the prompt to use for search (either this or project_id must be provided)
            project_id: ID of the project whose prompt to use (either this or prompt_id must be provided)
            num_videos: Number of video results to request (0-50)
            num_audio: Number of audio results to request (0-50)
            num_images: Number of image results to request (0-50)
            company_details: Company details to use for search context
            documents: List of document texts to use as additional context
            temperature: Custom temperature for the search query (0.0-1.0)
            
        Returns:
            Dictionary with job information
            
        Raises:
            ValueError: If neither prompt_id nor project_id is provided or parameters are invalid
        """
        if not prompt_id and not project_id:
            raise ValueError("Either prompt_id or project_id must be provided")
            
        # Validate numeric parameters
        try:
            num_videos = int(num_videos)
        except (TypeError, ValueError):
            raise ValueError(f"num_videos must be an integer between 0 and 50, got: {num_videos}")
            
        try:
            num_audio = int(num_audio)
        except (TypeError, ValueError):
            raise ValueError(f"num_audio must be an integer between 0 and 50, got: {num_audio}")
            
        try:
            num_images = int(num_images)
        except (TypeError, ValueError):
            raise ValueError(f"num_images must be an integer between 0 and 50, got: {num_images}")
            
        if temperature is not None:
            try:
                temperature = float(temperature)
            except (TypeError, ValueError):
                raise ValueError(f"temperature must be a number between 0 and 1, got: {temperature}")
                
            if temperature < 0 or temperature > 1:
                raise ValueError(f"temperature must be between 0 and 1, got: {temperature}")
                
        # Validate ranges
        if num_videos < 0 or num_videos > 50:
            raise ValueError(f"num_videos must be between 0 and 50, got: {num_videos}")
            
        if num_audio < 0 or num_audio > 50:
            raise ValueError(f"num_audio must be between 0 and 50, got: {num_audio}")
            
        if num_images < 0 or num_images > 50:
            raise ValueError(f"num_images must be between 0 and 50, got: {num_images}")
            
        # Ensure at least one content type is requested
        if num_videos == 0 and num_audio == 0 and num_images == 0:
            raise ValueError("At least one of num_videos, num_audio, or num_images must be greater than 0")
            
        # Prepare request data
        data = {
            "num_videos": num_videos,
            "num_audio": num_audio,
            "num_images": num_images
        }
        
        if prompt_id:
            data["prompt_id"] = prompt_id
        if project_id:
            data["project_id"] = project_id
        if company_details:
            data["company_details"] = company_details
        if documents:
            data["documents"] = documents
        if temperature is not None:
            data["temperature"] = temperature
            
        return self._make_request("POST", f"{self.prompts_url}/query/generate", json_data=data)
    
    def get_search_query_results(self, prompt_id: str = None, project_id: str = None, job_id: str = None) -> Dict:
        """
        Get results from a previously started search job.
        
        Args:
            prompt_id: ID of the prompt used for the search (either this or project_id must be provided)
            project_id: ID of the project whose prompt was used (either this or prompt_id must be provided)
            job_id: ID of the specific search job (optional, but recommended)
            
        Returns:
            Dictionary with search results or status
            
        Raises:
            ValueError: If neither prompt_id nor project_id is provided
        """
        if not prompt_id and not project_id:
            raise ValueError("Either prompt_id or project_id must be provided")
            
        params = {}
        if prompt_id:
            params["prompt_id"] = prompt_id
        if project_id:
            params["project_id"] = project_id
        if job_id:
            params["job_id"] = job_id
            
        return self._make_request("GET", f"{self.prompts_url}/query/results", params=params)
    
    def start_query_gen_and_wait(self, 
                        prompt_id: str = None, 
                        project_id: str = None, 
                        num_videos: int = 5, 
                        num_audio: int = 1, 
                        num_images: int = 0,
                        company_details: str = "", 
                        documents: List[str] = None,
                        temperature: float = None,
                        max_wait_seconds: int = 60,
                        poll_interval_seconds: int = 2) -> Dict:
        """
        Generate a content search and wait for results.
        
        Args:
            prompt_id: ID of the prompt to use for search
            project_id: ID of the project whose prompt to use
            num_videos: Number of videos to search for (0-50)
            num_audio: Number of audio files to search for (0-50)
            num_images: Number of images to search for (0-50)
            company_details: Company details to use for search context
            documents: List of document texts to use as additional context
            temperature: Temperature for the search (0.0-1.0)
            max_wait_seconds: Maximum time to wait for results in seconds
            poll_interval_seconds: Time between result check requests in seconds
            
        Returns:
            Dictionary with search results or the last status
            
        Raises:
            ValueError: If parameters are invalid
            TimeoutError: If search takes longer than max_wait_seconds
        """
        import time
        
        # Start the search
        search_response = self.generate_search_query(
            prompt_id=prompt_id,
            project_id=project_id,
            num_videos=num_videos,
            num_audio=num_audio,
            num_images=num_images,
            company_details=company_details,
            documents=documents,
            temperature=temperature
        )
        
        job_id = search_response.get("job_id")
        if not job_id:
            return search_response  # Return error or unexpected response
            
        # Poll for results
        elapsed = 0
        while elapsed < max_wait_seconds:
            results = self.get_search_query_results(
                prompt_id=prompt_id,
                project_id=project_id,
                job_id=job_id  # Pass the job_id to identify the specific search job
            )
            
            status = results.get("status")
            
            # If completed, return results
            if status == "COMPLETED":
                return results
                
            # Wait before polling again
            time.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds
            
        raise TimeoutError(f"Search did not complete within {max_wait_seconds} seconds. Last status: {results.get('status', 'unknown')}")
    
    def get_storage_usage(self, org_id: str = None) -> Dict:
        """
        Get storage usage information for an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with storage usage information
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        params = {"org_id": org_id}
        return self._make_request("GET", f"{self.prompts_url}/storage/usage", params=params)
