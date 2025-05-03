import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from .base_client import BaseClient

class UtilsClient(BaseClient):
    """
    Client for interacting with Storylinez Utility API.
    Provides methods for accessing common utilities and AI-powered helpers.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the UtilsClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.utils_url = f"{self.base_url}/utils"
    
    # Voice and Media Types
    
    def get_voice_types(self) -> Dict:
        """
        Get available voice types for voiceover generation.
        
        Returns:
            Dictionary with available voice types and their details
            
        Example:
            >>> client.utils.get_voice_types()
            {
                'message': 'Voice types retrieved successfully',
                'voice_types': {
                    'en': {'male': {...}, 'female': {...}},
                    'es': {'male': {...}, 'female': {...}}
                }
            }
        """
        return self._make_request("GET", f"{self.utils_url}/voice-types")
    
    def get_transition_types(self) -> Dict:
        """
        Get available transition types for video editing.
        
        Returns:
            Dictionary with available transition types and their details
            
        Example:
            >>> client.utils.get_transition_types()
            {
                'message': 'Transition types retrieved successfully',
                'transition_types': {
                    'fade': {'description': 'Smooth fade between scenes', ...},
                    'dissolve': {'description': 'Gradual dissolve transition', ...}
                }
            }
        """
        return self._make_request("GET", f"{self.utils_url}/transition-types")
    
    def get_template_types(self) -> Dict:
        """
        Get available template types for video styling.
        
        Returns:
            Dictionary with available template types and their details
            
        Example:
            >>> client.utils.get_template_types()
            {
                'message': 'Template types retrieved successfully',
                'template_types': {
                    'corporate': {'description': 'Professional business style', ...},
                    'social_media': {'description': 'Optimized for social platforms', ...}
                }
            }
        """
        return self._make_request("GET", f"{self.utils_url}/template-types")
    
    def get_color_grades(self) -> Dict:
        """
        Get available color grading options for video styling.
        
        Returns:
            Dictionary with available color grades and their details
            
        Example:
            >>> client.utils.get_color_grades()
            {
                'message': 'Color grades retrieved successfully',
                'color_grades': {
                    'single': [...],
                    'multiple': [...]
                }
            }
        """
        return self._make_request("GET", f"{self.utils_url}/color-grades")
    
    # AI Assistant Functions
    
    def alter_prompt(
        self, 
        old_prompt: str, 
        job_name: str = None,
        company_details: Union[str, Dict] = None,
        edited_json: Dict = None, 
        temperature: float = 0.7,
        alter_type: str = "enhance", 
        prompt_type: str = "prompt",
        org_id: str = None
    ) -> Dict:
        """
        Enhance or randomize an existing prompt.
        
        Args:
            old_prompt: The original prompt text to be altered
            job_name: Optional name for the alteration job
            company_details: Company context to consider (string or dictionary)
            edited_json: Optional previous generation/edited content
            temperature: AI temperature parameter (0.0-1.0)
            alter_type: Type of alteration to perform: "enhance" or "randomize"
            prompt_type: Type of prompt: "prompt", "storyboard", or "sequence"
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with job ID and status
            
        Raises:
            ValueError: If parameters are invalid
            
        Notes:
            - Use "enhance" to make prompts more detailed and effective
            - Use "randomize" to generate creative variations
            - Lower temperature (0.1-0.3) for conservative alterations
            - Higher temperature (0.7-1.0) for creative alterations
            
        Example:
            >>> result = client.utils.alter_prompt(
            ...     old_prompt="Create a video about our product features",
            ...     job_name="Product Video Enhancement",
            ...     company_details="Tech company focusing on AI solutions",
            ...     temperature=0.6
            ... )
            >>> job_id = result.get("job_id")
            >>> # Wait for job to complete
            >>> job_result = client.utils.get_job_result(job_id)
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if not old_prompt:
            raise ValueError("old_prompt is required and cannot be empty")
        
        # Validate alter_type and prompt_type
        if alter_type not in ["enhance", "randomize"]:
            raise ValueError("alter_type must be either 'enhance' or 'randomize'")
            
        if prompt_type not in ["prompt", "storyboard", "sequence"]:
            raise ValueError("prompt_type must be either 'prompt', 'storyboard', or 'sequence'")
        
        # Validate temperature
        if not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
            
        # Prepare request data
        data = {
            "old_prompt": old_prompt,
            "org_id": org_id,
            "temperature": temperature
        }
        
        if job_name:
            data["job_name"] = job_name
            
        if edited_json:
            data["edited_json"] = edited_json
            
        # Handle company_details as string or dict
        if company_details:
            if isinstance(company_details, dict):
                data["company_details"] = company_details
            else:
                data["company_details"] = str(company_details)
        
        # Query parameters
        params = {
            "alter_type": alter_type,
            "prompt_type": prompt_type
        }
        
        return self._make_request("POST", f"{self.utils_url}/alter-prompt", params=params, json_data=data)
    
    def search_recommendations(
        self, 
        user_query: str, 
        job_name: str = None,
        documents: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = False, 
        overdrive: bool = False,
        web_search: bool = False, 
        eco: bool = False,
        org_id: str = None
    ) -> Dict:
        """
        Get search term recommendations based on a user query.
        
        Args:
            user_query: The search query to get recommendations for
            job_name: Optional name for the job
            documents: Optional list of document contexts to consider
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with job ID and status
            
        Raises:
            ValueError: If parameters are invalid
            
        Notes:
            - Use deepthink for more comprehensive analysis
            - Use web_search for current information on trending topics
            - Lower temperature (≤0.5) for factual research
            - Higher temperature (≥0.7) for creative exploration
            
        Example:
            >>> result = client.utils.search_recommendations(
            ...     user_query="video marketing trends 2023",
            ...     job_name="Marketing Research",
            ...     web_search=True,
            ...     temperature=0.5
            ... )
            >>> job_id = result.get("job_id")
            >>> # Wait for job to complete
            >>> job_result = client.utils.get_job_result(job_id)
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if not user_query:
            raise ValueError("user_query is required and cannot be empty")
        
        # Validate temperature
        if not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
        
        # Check if parameters are compatible
        if eco and overdrive:
            raise ValueError("eco and overdrive modes cannot be used together")
        
        # Prepare request data
        data = {
            "user_query": user_query,
            "org_id": org_id,
            "temperature": temperature
        }
        
        if job_name:
            data["job_name"] = job_name
            
        # Validate documents format if provided
        if documents:
            if not isinstance(documents, list):
                raise ValueError("documents must be a list of dictionaries")
                
            for doc in documents:
                if not isinstance(doc, dict) or "content" not in doc:
                    raise ValueError("Each document must be a dictionary with at least a 'content' key")
            
            data["documents"] = documents
        
        # Query parameters
        params = {
            "deepthink": str(deepthink).lower(),
            "overdrive": str(overdrive).lower(),
            "web_search": str(web_search).lower(),
            "eco": str(eco).lower()
        }
        
        return self._make_request("POST", f"{self.utils_url}/search-recommendations", params=params, json_data=data)
    
    def get_organization_info(
        self, 
        website_url: str, 
        job_name: str = None,
        scraped_content: str = None, 
        documents: List[Dict] = None,
        chat_history: List[Dict] = None, 
        temperature: float = 0.7,
        deepthink: bool = True, 
        overdrive: bool = False,
        web_search: bool = False, 
        eco: bool = False,
        org_id: str = None
    ) -> Dict:
        """
        Extract organization information from a website URL.
        
        Args:
            website_url: The URL of the organization's website
            job_name: Optional name for the job
            scraped_content: Optional pre-scraped website content
            documents: Optional list of document contexts to consider
            chat_history: Optional list of previous interactions
            temperature: AI temperature parameter (0.0-1.0)
            deepthink: Enable advanced thinking for complex topics (defaults to True)
            overdrive: Enable maximum quality and detail
            web_search: Enable web search for up-to-date information
            eco: Enable eco mode for faster processing
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with job ID and status
            
        Raises:
            ValueError: If parameters are invalid
            
        Notes:
            - Provide the main company website URL for best results
            - web_search improves results with external information
            - For maximum accuracy, keep temperature at or below 0.5
            - Results include company name, description, industry, values, and tone
            
        Example:
            >>> result = client.utils.get_organization_info(
            ...     website_url="https://www.example.com",
            ...     job_name="Company Analysis",
            ...     web_search=True,
            ...     temperature=0.5
            ... )
            >>> job_id = result.get("job_id")
            >>> # Wait for job to complete
            >>> job_result = client.utils.get_job_result(job_id)
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate website URL
        if not website_url:
            raise ValueError("website_url is required")
            
        if not website_url.startswith(("http://", "https://")):
            raise ValueError("website_url must be a valid URL starting with http:// or https://")
        
        # Validate temperature
        if not (0.0 <= temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
        
        # Check if parameters are compatible
        if eco and overdrive:
            raise ValueError("eco and overdrive modes cannot be used together")
        
        # Prepare request data
        data = {
            "website_url": website_url,
            "org_id": org_id,
            "temperature": temperature
        }
        
        if job_name:
            data["job_name"] = job_name
            
        if scraped_content is not None:
            data["scraped_content"] = scraped_content
        
        # Validate documents format if provided
        if documents is not None:
            if not isinstance(documents, list):
                raise ValueError("documents must be a list of dictionaries")
                
            for doc in documents:
                if not isinstance(doc, dict) or "content" not in doc:
                    raise ValueError("Each document must be a dictionary with at least a 'content' key")
            
            data["documents"] = documents
        
        # Validate chat_history format if provided
        if chat_history is not None:
            if not isinstance(chat_history, list):
                raise ValueError("chat_history must be a list of dictionaries")
                
            for msg in chat_history:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    raise ValueError("Each chat message must contain 'role' and 'content' keys")
                if msg.get("role") not in ["user", "assistant"]:
                    raise ValueError("Chat message roles must be either 'user' or 'assistant'")
            
            data["chat_history"] = chat_history
        
        # Query parameters
        params = {
            "deepthink": str(deepthink).lower(),
            "overdrive": str(overdrive).lower(),
            "web_search": str(web_search).lower(),
            "eco": str(eco).lower()
        }
        
        return self._make_request("POST", f"{self.utils_url}/organization-info", params=params, json_data=data)
    
    # Job Management
    
    def get_job_result(self, job_id: str) -> Dict:
        """
        Get the result of a utility job.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            Dictionary with job details and results
            
        Raises:
            ValueError: If job_id is invalid
            
        Example:
            >>> job_result = client.utils.get_job_result("job_0123456789")
            >>> if job_result.get("status") == "completed":
            ...     result = job_result.get("result")
            ...     # Process result data
        """
        if not job_id:
            raise ValueError("job_id is required")
        
        # Basic format validation
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("job_id must be a non-empty string")
            
        params = {"job_id": job_id.strip()}
        return self._make_request("GET", f"{self.utils_url}/get-result", params=params)
    
    def list_jobs(
        self, 
        job_type: str = None, 
        page: int = 1, 
        limit: int = 20,
        org_id: str = None
    ) -> Dict:
        """
        List utility jobs for an organization.
        
        Args:
            job_type: Optional filter by job type: "alter_prompt", "search_recommendations", or "organization_info"
            page: Page number for pagination (starting from 1)
            limit: Number of items per page (max 100)
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with job list and pagination info
            
        Raises:
            ValueError: If parameters are invalid
            
        Example:
            >>> jobs = client.utils.list_jobs(job_type="alter_prompt", page=1, limit=10)
            >>> print(f"Found {jobs.get('total')} jobs")
            >>> for job in jobs.get('jobs', []):
            ...     print(f"{job.get('job_name')} - {job.get('created_at')}")
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Validate job_type if provided
        if job_type and job_type not in ["alter_prompt", "search_recommendations", "organization_info"]:
            raise ValueError("job_type must be one of: 'alter_prompt', 'search_recommendations', 'organization_info'")
        
        # Validate pagination parameters
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
            
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ValueError("limit must be an integer between 1 and 100")
        
        params = {
            "org_id": org_id,
            "page": page,
            "limit": limit
        }
        
        if job_type:
            params["job_type"] = job_type
            
        return self._make_request("GET", f"{self.utils_url}/list-jobs", params=params)
    
    # Convenience Methods
    
    def wait_for_job_completion(
        self, 
        job_id: str, 
        timeout_seconds: int = 60, 
        polling_interval: int = 2,
        callback=None
    ) -> Dict:
        """
        Wait for a job to complete with polling.
        
        Args:
            job_id: The ID of the job to wait for
            timeout_seconds: Maximum time to wait in seconds (0 for no timeout)
            polling_interval: Time between checks in seconds
            callback: Optional callback function receiving job status updates
            
        Returns:
            The completed job result dictionary
            
        Raises:
            TimeoutError: If job doesn't complete within timeout period
            ValueError: If job_id is invalid
            
        Example:
            >>> result = client.utils.alter_prompt(old_prompt="Create a video")
            >>> job_id = result.get("job_id")
            >>> try:
            ...     completed_job = client.utils.wait_for_job_completion(
            ...         job_id, 
            ...         timeout_seconds=30,
            ...         callback=lambda status: print(f"Job status: {status}")
            ...     )
            ...     print(f"Final result: {completed_job.get('result')}")
            ... except TimeoutError:
            ...     print("Job took too long to complete")
        """
        import time
        
        if not job_id:
            raise ValueError("job_id is required")
        
        start_time = time.time()
        last_job_state = None
        
        while timeout_seconds == 0 or (time.time() - start_time) < timeout_seconds:
            job_result = self.get_job_result(job_id)
            
            # Determine job state by checking the response structure
            current_job_state = "processing"  # Default state
            
            if "result" in job_result and job_result.get("result"):
                current_job_state = "completed"
            elif job_result.get("error") is not None:
                current_job_state = "failed"
            
            # Call callback if provided and state changed
            if callback and current_job_state != last_job_state:
                callback(current_job_state)
            last_job_state = current_job_state
            
            if current_job_state == "completed":
                return job_result
            elif current_job_state == "failed":
                raise Exception(f"Job failed: {job_result.get('error')}")
            
            # Wait before polling again
            time.sleep(polling_interval)
        
        raise TimeoutError(f"Job did not complete within {timeout_seconds} seconds")
    
    def enhance_prompt_and_wait(
        self, 
        prompt: str, 
        **kwargs
    ) -> str:
        """
        Enhance a prompt and wait for completion, returning the enhanced result.
        
        Args:
            prompt: The prompt to enhance
            **kwargs: Additional parameters to pass to alter_prompt method
            
        Returns:
            The enhanced prompt text
            
        Raises:
            TimeoutError: If job doesn't complete within timeout period
            ValueError: If parameters are invalid
            
        Example:
            >>> enhanced = client.utils.enhance_prompt_and_wait(
            ...     "Create a video about our product",
            ...     company_details="Tech startup with AI focus",
            ...     timeout_seconds=30
            ... )
            >>> print(f"Enhanced prompt: {enhanced}")
        """
        # Extract timeout parameters
        timeout_seconds = kwargs.pop("timeout_seconds", 60)
        polling_interval = kwargs.pop("polling_interval", 2)
        callback = kwargs.pop("callback", None)
        
        # Start the job
        result = self.alter_prompt(
            old_prompt=prompt,
            alter_type="enhance",
            **kwargs
        )
        
        job_id = result.get("job_id")
        
        # Wait for completion
        completed_job = self.wait_for_job_completion(
            job_id,
            timeout_seconds=timeout_seconds,
            polling_interval=polling_interval,
            callback=callback
        )
        
        # Extract and return the enhanced prompt
        result_data = completed_job.get("result", {})
        return result_data.get("prompt", "")  # Return the enhanced prompt
