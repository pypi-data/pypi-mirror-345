import os
import json
import requests
from typing import Dict, List, Optional, Union, Any, Tuple
import warnings
from .base_client import BaseClient

class ToolsClient(BaseClient):
    """
    Client for interacting with Storylinez Tools API.
    Provides methods for creating and managing AI-powered creative tools.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the ToolsClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.tools_url = f"{self.base_url}/tools"
        
        # Valid video formats for scene_splitter
        self.valid_video_formats = ["mp4", "mov", "avi", "mkv", "webm"]
        
        # Tool types for validation
        self.valid_tool_types = [
            "creative_brief",
            "audience_research",
            "video_plan",
            "shotlist",
            "ad_concept",
            "scene_transitions",
            "scene_splitter"
        ]
    
    def get_tool_types(self) -> Dict:
        """
        Get a list of available tool types.
        
        Returns:
            Dictionary with available tool types and their names
            
        Example:
            >>> client.tools.get_tool_types()
            {
                'message': 'Tool types retrieved successfully',
                'tool_types': [
                    {'type': 'creative_brief', 'name': 'Creative Brief'},
                    {'type': 'audience_research', 'name': 'Audience Research'},
                    # ...other tool types
                ],
                'count': 7
            }
        """
        return self._make_request("GET", f"{self.tools_url}/types")
    
    def _validate_org_id(self, org_id: str = None) -> str:
        """
        Validate and return organization ID.
        
        Args:
            org_id: Organization ID to validate or None to use default
            
        Returns:
            Validated organization ID
            
        Raises:
            ValueError: If no valid organization ID is available
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        return org_id
    
    def _validate_temperature(self, temperature: float) -> float:
        """
        Validate temperature parameter is within acceptable range.
        
        Args:
            temperature: Temperature value to validate
            
        Returns:
            Validated temperature value
            
        Raises:
            ValueError: If temperature is outside valid range
        """
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                raise ValueError("Temperature must be a number")
            if temperature < 0.0 or temperature > 1.0:
                raise ValueError("Temperature must be between 0.0 and 1.0")
        return temperature
    
    def _format_document_list(self, documents: Any) -> List[Dict]:
        """
        Validate and format document list for API requests.
        
        Args:
            documents: Document list to validate and format
            
        Returns:
            Formatted document list
            
        Raises:
            ValueError: If documents parameter is invalid
        """
        if documents is None:
            return None
            
        if not isinstance(documents, list):
            raise ValueError("Documents must be a list of dictionaries with 'name' and 'content' fields")
            
        for doc in documents:
            if not isinstance(doc, dict):
                raise ValueError("Each document must be a dictionary")
            if 'name' not in doc or 'content' not in doc:
                raise ValueError("Each document must contain 'name' and 'content' fields")
                
        return documents
    
    # Creative Brief Tool
    
    def create_creative_brief(
        self, 
        name: str, 
        user_input: str, 
        org_id: str = None,
        company_details: str = None, 
        auto_company_details: bool = True,
        company_details_id: str = None, 
        documents: List[Dict] = None, 
        temperature: float = 0.7, 
        deepthink: bool = False, 
        overdrive: bool = False, 
        web_search: bool = False, 
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create a creative brief using AI.
        
        Args:
            name: Name for the creative brief
            user_input: Main user instructions or requirements
            org_id: Organization ID (uses default if not provided)
            company_details: Company details as text (ignored if auto_company_details=True)
            auto_company_details: Whether to automatically fetch company details
            company_details_id: Specific company details ID to use (if auto_company_details=True)
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_creative_brief(
            ...     name="Q4 Campaign Brief",
            ...     user_input="Create a creative brief for our new summer product line",
            ...     deepthink=True
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not user_input:
            raise ValueError("User input is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Auto-company details logic
        if auto_company_details:
            if company_details:
                warnings.warn(
                    "Both auto_company_details=True and company_details provided. "
                    "The auto-populated company details will be used instead of the provided company_details.",
                    UserWarning
                )
                
        data = {
            "tool_type": "creative_brief",
            "org_id": org_id,
            "name": name,
            "user_input": user_input,
            "company_details": company_details,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "web_search": web_search,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Audience Research Tool
    
    def create_audience_research(
        self,
        name: str, 
        user_input: str, 
        org_id: str = None,
        company_details: str = None, 
        auto_company_details: bool = True,
        company_details_id: str = None, 
        additional_context: str = None,
        documents: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = True, 
        overdrive: bool = True, 
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create audience research using AI.
        
        Args:
            name: Name for the audience research
            user_input: Main user instructions or audience to research
            org_id: Organization ID (uses default if not provided)
            company_details: Company details as text (ignored if auto_company_details=True)
            auto_company_details: Whether to automatically fetch company details
            company_details_id: Specific company details ID to use (if auto_company_details=True)
            additional_context: Extra context about the target audience
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics (defaults to True)
            overdrive: Enable maximum quality and detail (defaults to True)
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_audience_research(
            ...     name="Gen Z Market Analysis",
            ...     user_input="Research the Gen Z audience and their preferences",
            ...     additional_context="Focus on 18-24 year olds in urban areas"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not user_input:
            raise ValueError("User input is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Auto-company details logic
        if auto_company_details and company_details:
            warnings.warn(
                "Both auto_company_details=True and company_details provided. "
                "The auto-populated company details will be used instead of the provided company_details.",
                UserWarning
            )
                
        data = {
            "tool_type": "audience_research",
            "org_id": org_id,
            "name": name,
            "user_input": user_input,
            "company_details": company_details,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "additional_context": additional_context,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Video Plan Tool
    
    def create_video_plan(
        self,
        name: str, 
        user_input: str, 
        org_id: str = None,
        company_details: str = None, 
        auto_company_details: bool = True,
        company_details_id: str = None, 
        additional_context: str = None,
        documents: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = True, 
        overdrive: bool = True, 
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create a video plan using AI.
        
        Args:
            name: Name for the video plan
            user_input: Main user instructions for video planning
            org_id: Organization ID (uses default if not provided)
            company_details: Company details as text (ignored if auto_company_details=True)
            auto_company_details: Whether to automatically fetch company details
            company_details_id: Specific company details ID to use (if auto_company_details=True)
            additional_context: Extra context about the video requirements
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics (defaults to True)
            overdrive: Enable maximum quality and detail (defaults to True)
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_video_plan(
            ...     name="Brand Introduction Video",
            ...     user_input="Create a video plan for introducing our new brand",
            ...     additional_context="Focus on our sustainability efforts"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not user_input:
            raise ValueError("User input is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Auto-company details logic
        if auto_company_details and company_details:
            warnings.warn(
                "Both auto_company_details=True and company_details provided. "
                "The auto-populated company details will be used instead of the provided company_details.",
                UserWarning
            )
                
        data = {
            "tool_type": "video_plan",
            "org_id": org_id,
            "name": name,
            "user_input": user_input,
            "company_details": company_details,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "additional_context": additional_context,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Shotlist Tool
    
    def create_shotlist(
        self,
        name: str, 
        user_input: str, 
        org_id: str = None,
        scene_details: str = None, 
        visual_style: str = None,
        documents: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = False, 
        overdrive: bool = False,
        web_search: bool = False, 
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create a shotlist using AI.
        
        Args:
            name: Name for the shotlist
            user_input: Main user instructions for shotlist creation
            org_id: Organization ID (uses default if not provided)
            scene_details: Details about the scenes to be shot
            visual_style: Description of the visual style
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_shotlist(
            ...     name="Product Demo Shotlist",
            ...     user_input="Create a shotlist for our product demo video",
            ...     scene_details="Indoor office environment with good natural lighting",
            ...     visual_style="Clean, professional, with smooth camera movements"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not user_input:
            raise ValueError("User input is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Provide helpful tips
        if not scene_details:
            warnings.warn(
                "No scene_details provided. Adding scene details will improve shotlist quality.",
                UserWarning
            )
        
        if not visual_style:
            warnings.warn(
                "No visual_style provided. Adding visual style information will improve shotlist quality.",
                UserWarning
            )
                
        data = {
            "tool_type": "shotlist",
            "org_id": org_id,
            "name": name,
            "user_input": user_input,
            "scene_details": scene_details,
            "visual_style": visual_style,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "web_search": web_search,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Ad Concept Tool
    
    def create_ad_concept(
        self,
        name: str, 
        user_input: str, 
        org_id: str = None,
        brand_details: str = None, 
        auto_company_details: bool = True,
        company_details_id: str = None, 
        campaign_goals: str = None,
        target_audience: str = None, 
        documents: List[Dict] = None,
        temperature: float = 0.7, 
        deepthink: bool = True,
        overdrive: bool = True, 
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create an ad concept using AI.
        
        Args:
            name: Name for the ad concept
            user_input: Main user instructions for ad concept
            org_id: Organization ID (uses default if not provided)
            brand_details: Brand details as text (ignored if auto_company_details=True)
            auto_company_details: Whether to automatically fetch company details as brand details
            company_details_id: Specific company details ID to use (if auto_company_details=True)
            campaign_goals: Goals of the advertising campaign
            target_audience: Description of the target audience
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics (defaults to True)
            overdrive: Enable maximum quality and detail (defaults to True)
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_ad_concept(
            ...     name="Summer Sale Campaign",
            ...     user_input="Create an ad concept for our summer sale",
            ...     campaign_goals="Increase summer sales by 25%",
            ...     target_audience="Young professionals, 25-40, with disposable income"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not user_input:
            raise ValueError("User input is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Auto-company details logic
        if auto_company_details and brand_details:
            warnings.warn(
                "Both auto_company_details=True and brand_details provided. "
                "The auto-populated brand details will be used instead of the provided brand_details.",
                UserWarning
            )
        
        # Provide helpful tips
        if not campaign_goals:
            warnings.warn(
                "No campaign_goals provided. Adding specific goals will improve ad concept quality.",
                UserWarning
            )
            
        if not target_audience:
            warnings.warn(
                "No target_audience provided. Adding target audience details will improve ad concept focus.",
                UserWarning
            )
                
        data = {
            "tool_type": "ad_concept",
            "org_id": org_id,
            "name": name,
            "user_input": user_input,
            "brand_details": brand_details,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "campaign_goals": campaign_goals,
            "target_audience": target_audience,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Scene Transitions Tool
    
    def create_scene_transitions(
        self,
        name: str, 
        scene_descriptions: List[str],
        org_id: str = None, 
        project_style: str = None,
        mood: str = None, 
        brand_guidelines: str = None,
        auto_company_details: bool = True, 
        company_details_id: str = None,
        documents: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = True, 
        overdrive: bool = True,
        eco: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create scene transitions using AI.
        
        Args:
            name: Name for the scene transitions
            scene_descriptions: List of scene descriptions to transition between (minimum 2)
            org_id: Organization ID (uses default if not provided)
            project_style: Style of the overall project
            mood: Mood or tone of the transitions
            brand_guidelines: Brand guidelines as text (ignored if auto_company_details=True)
            auto_company_details: Whether to automatically fetch company details as brand guidelines
            company_details_id: Specific company details ID to use (if auto_company_details=True)
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics (defaults to True)
            overdrive: Enable maximum quality and detail (defaults to True)
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_scene_transitions(
            ...     name="Product Journey Transitions",
            ...     scene_descriptions=[
            ...         "Raw materials being harvested sustainably",
            ...         "Manufacturing process with eco-friendly methods",
            ...         "Customer unboxing and using the product"
            ...     ],
            ...     project_style="Documentary style with cinematic quality",
            ...     mood="Inspiring and educational"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
            
        # Validate scene_descriptions
        if not scene_descriptions:
            raise ValueError("scene_descriptions is required")
        if not isinstance(scene_descriptions, list):
            raise ValueError("scene_descriptions must be a list")
        if len(scene_descriptions) < 2:
            raise ValueError("scene_descriptions must contain at least 2 scenes")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate temperature
        temperature = self._validate_temperature(temperature)
        
        # Format documents
        documents = self._format_document_list(documents)
        
        # Auto-company details logic
        if auto_company_details and brand_guidelines:
            warnings.warn(
                "Both auto_company_details=True and brand_guidelines provided. "
                "The auto-populated brand guidelines will be used instead of the provided brand_guidelines.",
                UserWarning
            )
        
        # Provide helpful tips
        if not project_style:
            warnings.warn(
                "No project_style provided. Adding project style information will improve transition quality.",
                UserWarning
            )
            
        if not mood:
            warnings.warn(
                "No mood provided. Adding mood information will help set the appropriate tone for transitions.",
                UserWarning
            )
                
        data = {
            "tool_type": "scene_transitions",
            "org_id": org_id,
            "name": name,
            "scene_descriptions": scene_descriptions,
            "project_style": project_style,
            "mood": mood,
            "brand_guidelines": brand_guidelines,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "documents": documents,
            "temperature": temperature,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "eco": eco
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Scene Splitter Tool
    
    def create_scene_splitter(
        self,
        name: str, 
        video_path: str, 
        bucket_name: str,
        org_id: str = None,
        **kwargs
    ) -> Dict:
        """
        Split a video into scenes automatically.
        
        Args:
            name: Name for the scene splitter job
            video_path: Path to the video file in S3
            bucket_name: S3 bucket name where the video is stored
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and job information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.create_scene_splitter(
            ...     name="Product Demo Scene Analysis",
            ...     video_path="userdata/my_org/videos/product_demo.mp4",
            ...     bucket_name="storylinez-media"
            ... )
        """
        # Validate required parameters
        if not name:
            raise ValueError("Name is required")
        if not video_path:
            raise ValueError("video_path is required")
        if not bucket_name:
            raise ValueError("bucket_name is required")
            
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate video file extension
        _, ext = os.path.splitext(video_path)
        ext = ext.lower().lstrip('.')
        
        if not ext or ext not in self.valid_video_formats:
            raise ValueError(
                f"Invalid video file extension: {ext if ext else 'none'}. "
                f"Supported formats are: {', '.join(self.valid_video_formats)}"
            )
                
        data = {
            "tool_type": "scene_splitter",
            "org_id": org_id,
            "name": name,
            "video_path": video_path,
            "bucket_name": bucket_name
        }
        
        # Add any additional parameters from kwargs
        data.update(kwargs)
        
        return self._make_request("POST", f"{self.tools_url}/create", json_data=data)
    
    # Tool Management Methods
    
    def get_tool(self, tool_id: str, include_job: bool = True, **kwargs) -> Dict:
        """
        Get details about a specific tool.
        
        Args:
            tool_id: ID of the tool to retrieve
            include_job: Whether to include the job result data
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tool details and optionally job results
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.get_tool(tool_id="550e8400-e29b-41d4-a716-446655440000")
        """
        if not tool_id:
            raise ValueError("tool_id is required")
            
        params = {
            "tool_id": tool_id,
            "include_job": str(include_job).lower()
        }
        
        # Add any additional parameters from kwargs
        params.update(kwargs)
        
        return self._make_request("GET", f"{self.tools_url}/get", params=params)
    
    def list_tools(
        self,
        org_id: str = None, 
        tool_type: str = None, 
        include_results: bool = False,
        page: int = 1, 
        limit: int = 20,
        **kwargs
    ) -> Dict:
        """
        List tools for an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            tool_type: Optional filter by tool type
            include_results: Whether to include job results for each tool
            page: Page number for pagination (starts at 1)
            limit: Number of items per page (max 100)
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with tools list and pagination info
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.list_tools(tool_type="creative_brief", limit=10)
        """
        # Validate org_id
        org_id = self._validate_org_id(org_id)
        
        # Validate tool_type if provided
        if tool_type is not None and tool_type not in self.valid_tool_types:
            raise ValueError(f"Invalid tool_type. Must be one of: {', '.join(self.valid_tool_types)}")
        
        # Validate pagination parameters
        try:
            page = int(page)
            limit = int(limit)
            
            if page < 1:
                raise ValueError("Page number must be at least 1")
                
            if limit < 1:
                raise ValueError("Limit must be at least 1")
                
            if limit > 100:
                warnings.warn(
                    f"Limit exceeds maximum value of 100. It will be capped to 100.",
                    UserWarning
                )
                limit = 100
        except (ValueError, TypeError):
            raise ValueError("Page and limit must be valid integers")
        
        params = {
            "org_id": org_id,
            "include_results": str(include_results).lower(),
            "page": page,
            "limit": limit
        }
        
        if tool_type:
            params["tool_type"] = tool_type
        
        # Add any additional parameters from kwargs
        params.update(kwargs)
            
        return self._make_request("GET", f"{self.tools_url}/list", params=params)
    
    def update_tool(self, tool_id: str, name: str = None, tags: List[str] = None, **kwargs) -> Dict:
        """
        Update a tool's metadata.
        
        Args:
            tool_id: ID of the tool to update
            name: New name for the tool
            tags: List of tags for the tool
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with updated tool information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.update_tool(
            ...     tool_id="550e8400-e29b-41d4-a716-446655440000",
            ...     name="Updated Brief Name",
            ...     tags=["marketing", "summer", "campaign"]
            ... )
        """
        if not tool_id:
            raise ValueError("tool_id is required")
            
        data = {
            "tool_id": tool_id
        }
        
        if name is not None:
            data["name"] = name
            
        if tags is not None:
            if not isinstance(tags, list):
                raise ValueError("Tags must be provided as a list of strings")
            data["tags"] = tags
            
        if len(data) <= 1:
            raise ValueError("At least one updatable field (name or tags) must be provided")
            
        # Add any additional parameters from kwargs
        data.update(kwargs)
            
        return self._make_request("PUT", f"{self.tools_url}/update", json_data=data)
    
    def delete_tool(self, tool_id: str, **kwargs) -> Dict:
        """
        Delete a tool.
        
        Args:
            tool_id: ID of the tool to delete
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with deletion confirmation
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.delete_tool(tool_id="550e8400-e29b-41d4-a716-446655440000")
        """
        if not tool_id:
            raise ValueError("tool_id is required")
            
        params = {
            "tool_id": tool_id
        }
        
        # Add any additional parameters from kwargs
        params.update(kwargs)
        
        return self._make_request("DELETE", f"{self.tools_url}/delete", params=params)
    
    def redo_tool(
        self,
        tool_id: str, 
        input_data: Dict = None, 
        auto_company_details: bool = None,
        company_details_id: str = None, 
        deepthink: bool = None, 
        overdrive: bool = None,
        web_search: bool = None, 
        eco: bool = None,
        **kwargs
    ) -> Dict:
        """
        Restart a tool job with potentially modified parameters.
        
        Args:
            tool_id: ID of the tool to redo
            input_data: Optional dictionary of input data to override
            auto_company_details: Whether to automatically fetch company details
            company_details_id: Specific company details ID to use
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            **kwargs: Additional parameters to pass directly to the API
            
        Returns:
            Dictionary with job information for the restarted job
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> client.tools.redo_tool(
            ...     tool_id="550e8400-e29b-41d4-a716-446655440000",
            ...     input_data={"user_input": "Updated prompt for the creative brief"},
            ...     deepthink=True
            ... )
        """
        if not tool_id:
            raise ValueError("tool_id is required")
            
        data = {
            "tool_id": tool_id
        }
        
        if input_data is not None:
            if not isinstance(input_data, dict):
                raise ValueError("input_data must be a dictionary")
            data["input_data"] = input_data
            
        if auto_company_details is not None:
            data["auto_company_details"] = auto_company_details
            
        if company_details_id is not None:
            data["company_details_id"] = company_details_id
            
        if deepthink is not None:
            data["deepthink"] = deepthink
            
        if overdrive is not None:
            data["overdrive"] = overdrive
            
        if web_search is not None:
            data["web_search"] = web_search
            
        if eco is not None:
            data["eco"] = eco
            
        # Add any additional parameters from kwargs
        data.update(kwargs)
            
        return self._make_request("POST", f"{self.tools_url}/redo", json_data=data)
        
    # --- Additional utility methods and workflows ---
    
    def wait_for_tool_completion(
        self,
        tool_id: str,
        max_wait_time: int = 120,
        polling_interval: int = 2
    ) -> Dict:
        """
        Wait for a tool job to complete, with timeout.
        
        Args:
            tool_id: ID of the tool to wait for
            max_wait_time: Maximum time to wait in seconds
            polling_interval: Time between status checks in seconds
            
        Returns:
            Dictionary with the completed tool data including job result
            
        Raises:
            TimeoutError: If the tool doesn't complete within max_wait_time
            ValueError: If tool_id is invalid or not found
            
        Example:
            >>> result = client.tools.create_creative_brief(name="Test Brief", user_input="Create a brief")
            >>> tool_id = result["tool"]["tool_id"]
            >>> completed_tool = client.tools.wait_for_tool_completion(tool_id)
        """
        import time
        
        if not tool_id:
            raise ValueError("tool_id is required")
            
        start_time = time.time()
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            tool_data = self.get_tool(tool_id)
            
            if "job_result" in tool_data:
                job_result = tool_data.get("job_result", {})
                status = job_result.get("status", "").upper()
                
                if status == "COMPLETED":
                    return tool_data
                    
                if status == "ERROR" or status == "FAILED":
                    error_message = job_result.get("error", "Unknown error")
                    raise ValueError(f"Tool job failed: {error_message}")
            
            # Wait before checking again
            time.sleep(polling_interval)
            elapsed_time = time.time() - start_time
            
        raise TimeoutError(f"Tool job did not complete within {max_wait_time} seconds")
        
    def create_and_wait(
        self,
        tool_type: str,
        name: str,
        **kwargs
    ) -> Dict:
        """
        Create a tool and wait for it to complete.
        
        Args:
            tool_type: Type of tool to create
            name: Name for the tool
            **kwargs: Parameters specific to the tool type
            
        Returns:
            Dictionary with the completed tool data
            
        Raises:
            ValueError: If required parameters are missing or invalid
            
        Example:
            >>> completed_tool = client.tools.create_and_wait(
            ...     tool_type="creative_brief",
            ...     name="Urgent Campaign Brief",
            ...     user_input="Create a brief for our holiday campaign",
            ...     max_wait_time=180  # Wait up to 3 minutes
            ... )
        """
        if not tool_type:
            raise ValueError("tool_type is required")
            
        if not name:
            raise ValueError("name is required")
            
        # Extract wait parameters
        max_wait_time = kwargs.pop("max_wait_time", 120)
        polling_interval = kwargs.pop("polling_interval", 2)
        
        # Validate tool type
        if tool_type not in self.valid_tool_types:
            raise ValueError(f"Invalid tool_type. Must be one of: {', '.join(self.valid_tool_types)}")
        
        # Call the appropriate method based on tool_type
        creation_methods = {
            "creative_brief": self.create_creative_brief,
            "audience_research": self.create_audience_research,
            "video_plan": self.create_video_plan,
            "shotlist": self.create_shotlist,
            "ad_concept": self.create_ad_concept,
            "scene_transitions": self.create_scene_transitions,
            "scene_splitter": self.create_scene_splitter
        }
        
        # Create the tool
        result = creation_methods[tool_type](name=name, **kwargs)
        tool_id = result.get("tool", {}).get("tool_id")
        
        if not tool_id:
            raise ValueError("Failed to get tool_id from creation result")
            
        # Wait for completion
        return self.wait_for_tool_completion(
            tool_id=tool_id,
            max_wait_time=max_wait_time,
            polling_interval=polling_interval
        )
