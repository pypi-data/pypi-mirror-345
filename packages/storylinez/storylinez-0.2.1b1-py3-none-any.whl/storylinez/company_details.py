import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from .base_client import BaseClient

class CompanyDetailsClient(BaseClient):
    """
    Client for interacting with Storylinez Company Details API.
    Provides methods for managing company details/profiles.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the CompanyDetailsClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.company_url = f"{self.base_url}/company"
    
    def create(self, 
               company_name: str, 
               company_type: str = "", 
               tag_line: str = "", 
               vision: str = "",
               products: str = "", 
               description: str = "",
               cta_text: str = "", 
               cta_subtext: str = "",
               link: str = "", 
               is_default: bool = False,
               others: Dict = None,
               org_id: str = None,
               **kwargs) -> Dict:
        """
        Create a new company details profile.
        
        Args:
            company_name: Name of the company (required)
            company_type: Type of company (e.g., "Software", "Healthcare")
            tag_line: Company's tag line or slogan
            vision: Company's vision statement
            products: Description of company's products or services
            description: Detailed company description
            cta_text: Call to action text
            cta_subtext: Call to action subtext
            link: Company website or relevant link
            is_default: Whether to set as the default company details
            others: Additional custom fields as a dictionary
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the created company details
            
        Raises:
            ValueError: If company_name is empty or org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if not company_name or not isinstance(company_name, str):
            raise ValueError("company_name is required and must be a string")
            
        # Input validation
        if not isinstance(is_default, bool):
            is_default = bool(is_default)
            
        # Make sure others is a dictionary if provided
        if others is not None and not isinstance(others, dict):
            raise TypeError("others must be a dictionary")
            
        data = {
            "org_id": org_id,
            "company_name": company_name,
            "company_type": str(company_type),
            "tag_line": str(tag_line),
            "vision": str(vision),
            "products": str(products),
            "description": str(description),
            "cta_text": str(cta_text),
            "cta_subtext": str(cta_subtext),
            "link": str(link),
            "is_default": is_default,
        }
        
        if others:
            data["others"] = others
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            data[key] = value
        
        return self._make_request("POST", f"{self.company_url}/create", json_data=data)
    
    def get_all(self, 
                page: int = 1, 
                limit: int = 10, 
                sort_by: str = "created_at", 
                order: str = "desc", 
                org_id: str = None,
                **kwargs) -> Dict:
        """
        Get all company details profiles for an organization with pagination.
        
        Args:
            page: Page number to retrieve (starts from 1)
            limit: Number of items per page (max 100)
            sort_by: Field to sort by (created_at, company_name, type, updated_at, etc.)
            order: Sort order (asc or desc)
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            Dictionary with company details list and pagination info
            
        Raises:
            ValueError: If page or limit are invalid or org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        # Input validation with helpful messages
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer starting from 1")
            
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        elif limit > 100:
            print("Warning: Maximum limit is 100. Your request will be capped at 100 items.")
            limit = 100
            
        # Validate sort_by against allowed fields
        allowed_sort_fields = ['company_name', 'type', 'created_at', 'updated_at', 
                               'tag_line', 'company_type', 'is_default']
        if sort_by not in allowed_sort_fields:
            print(f"Warning: '{sort_by}' is not a recognized sort field. Using 'created_at' instead.")
            print(f"Valid sort fields are: {', '.join(allowed_sort_fields)}")
            sort_by = 'created_at'
            
        # Validate order
        if order.lower() not in ['asc', 'desc']:
            print(f"Warning: '{order}' is not a valid sort order. Using 'desc' instead.")
            order = 'desc'
            
        params = {
            "org_id": org_id,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "order": order.lower()
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
        
        return self._make_request("GET", f"{self.company_url}/get_all", params=params)
    
    def get_one(self, 
                company_details_id: str = None, 
                org_id: str = None,
                **kwargs) -> Dict:
        """
        Get a specific company details profile or the default for an organization.
        
        Args:
            company_details_id: ID of the company details (if None, gets default)
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            Dictionary with the company details
            
        Raises:
            ValueError: If neither company_details_id nor org_id is provided
        """
        org_id = org_id or self.default_org_id
        
        if not company_details_id and not org_id:
            raise ValueError("Either company_details_id or org_id is required")
            
        params = {}
        if company_details_id:
            if not isinstance(company_details_id, str):
                raise TypeError("company_details_id must be a string")
            params["company_details_id"] = company_details_id
            
        if org_id:
            params["org_id"] = org_id
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
        
        return self._make_request("GET", f"{self.company_url}/get_one", params=params)
    
    def get_default(self, org_id: str = None, **kwargs) -> Dict:
        """
        Get the default company details for an organization.
        This is a convenience wrapper around get_one with is_default=True.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the default company details
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        params = {"org_id": org_id}
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
            
        return self._make_request("GET", f"{self.company_url}/get_default", params=params)
    
    def update(self, 
              company_details_id: str, 
              company_name: str = None,
              company_type: str = None, 
              tag_line: str = None,
              vision: str = None,
              products: str = None,
              description: str = None,
              cta_text: str = None,
              cta_subtext: str = None,
              link: str = None,
              is_default: bool = None,
              others: Dict = None,
              **kwargs) -> Dict:
        """
        Update a company details profile.
        
        Args:
            company_details_id: ID of the company details to update
            company_name: Name of the company
            company_type: Type of company
            tag_line: Company's tag line or slogan
            vision: Company's vision statement
            products: Description of company's products or services
            description: Detailed company description
            cta_text: Call to action text
            cta_subtext: Call to action subtext
            link: Company website or relevant link
            is_default: Whether to set as the default company details
            others: Additional custom fields
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the updated company details
            
        Raises:
            ValueError: If company_details_id is not provided or no update fields are specified
        """
        if not company_details_id:
            raise ValueError("company_details_id is required")
            
        data = {}
        
        # Process all the optional parameters, only including non-None values
        if company_name is not None:
            data["company_name"] = str(company_name)
        if company_type is not None:
            data["company_type"] = str(company_type)
        if tag_line is not None:
            data["tag_line"] = str(tag_line)
        if vision is not None:
            data["vision"] = str(vision)
        if products is not None:
            data["products"] = str(products)
        if description is not None:
            data["description"] = str(description)
        if cta_text is not None:
            data["cta_text"] = str(cta_text)
        if cta_subtext is not None:
            data["cta_subtext"] = str(cta_subtext)
        if link is not None:
            data["link"] = str(link)
        if is_default is not None:
            if not isinstance(is_default, bool):
                is_default = bool(is_default)
            data["is_default"] = is_default
            
        if others is not None:
            if not isinstance(others, dict):
                raise TypeError("others must be a dictionary")
            data["others"] = others
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            data[key] = value
            
        if not data:
            raise ValueError("At least one field to update must be provided")
            
        params = {"company_details_id": company_details_id}
        return self._make_request("PUT", f"{self.company_url}/update", params=params, json_data=data)
    
    def delete(self, company_details_id: str, **kwargs) -> Dict:
        """
        Delete a company details profile.
        
        Args:
            company_details_id: ID of the company details to delete
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with deletion confirmation
            
        Raises:
            ValueError: If company_details_id is not provided
        """
        if not company_details_id:
            raise ValueError("company_details_id is required")
            
        params = {"company_details_id": company_details_id}
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
            
        return self._make_request("DELETE", f"{self.company_url}/delete", params=params)
    
    def set_default(self, company_details_id: str, **kwargs) -> Dict:
        """
        Set a company details profile as the default.
        
        Args:
            company_details_id: ID of the company details to set as default
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with confirmation message
            
        Raises:
            ValueError: If company_details_id is not provided
        """
        if not company_details_id:
            raise ValueError("company_details_id is required")
            
        params = {"company_details_id": company_details_id}
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
            
        return self._make_request("PUT", f"{self.company_url}/set_default", params=params)
    
    def duplicate(self, 
                 company_details_id: str, 
                 company_name: str = None, 
                 org_id: str = None,
                 **kwargs) -> Dict:
        """
        Duplicate a company details profile.
        
        Args:
            company_details_id: ID of the company details to duplicate
            company_name: New name for the duplicated company details (optional)
            org_id: Organization ID for the duplicated company details
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the duplicated company details
            
        Raises:
            ValueError: If company_details_id or org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not company_details_id:
            raise ValueError("company_details_id is required")
            
        data = {
            "company_details_id": company_details_id,
            "org_id": org_id
        }
        
        if company_name is not None:
            data["company_name"] = str(company_name)
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            data[key] = value
            
        return self._make_request("POST", f"{self.company_url}/duplicate", json_data=data)
    
    def search(self, 
              query: str, 
              field: str = "company_name", 
              page: int = 1, 
              limit: int = 10, 
              sort_by: str = "created_at", 
              order: str = "desc", 
              org_id: str = None,
              **kwargs) -> Dict:
        """
        Search for company details profiles.
        
        Args:
            query: Search term
            field: Field to search in (company_name, tag_line, etc.)
            page: Page number to retrieve (starts from 1)
            limit: Number of items per page (max 100)
            sort_by: Field to sort by
            order: Sort order (asc or desc)
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Raises:
            ValueError: If org_id is not provided or page/limit are invalid
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Input validation
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer starting from 1")
            
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        elif limit > 100:
            print("Warning: Maximum limit is 100. Your request will be capped at 100 items.")
            limit = 100
            
        # Verify the search field is valid
        allowed_search_fields = [
            'company_name', 'type', 'tag_line', 'company_type', 
            'vision', 'products', 'description'
        ]
        
        if field not in allowed_search_fields:
            print(f"Warning: '{field}' is not a recognized search field. Using 'company_name' instead.")
            print(f"Valid search fields are: {', '.join(allowed_search_fields)}")
            field = 'company_name'
            
        # Validate order
        if order.lower() not in ['asc', 'desc']:
            print(f"Warning: '{order}' is not a valid sort order. Using 'desc' instead.")
            order = 'desc'
            
        params = {
            "org_id": org_id,
            "q": query,
            "field": field,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "order": order.lower()
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            params[key] = value
            
        return self._make_request("GET", f"{self.company_url}/search", params=params)

    def find_or_create_default_company(self, 
                                      company_name: str = None,
                                      create_if_missing: bool = True,
                                      company_type: str = "",
                                      tag_line: str = "", 
                                      vision: str = "",
                                      products: str = "", 
                                      description: str = "",
                                      org_id: str = None,
                                      **kwargs) -> Dict:
        """
        Find the default company details or create it if it doesn't exist.
        This is a convenience workflow that combines multiple API calls.
        
        Args:
            company_name: Name for the company if one needs to be created
            create_if_missing: Whether to create a company if none exists (True)
            company_type: Type of company for creation
            tag_line: Company's tag line for creation
            vision: Company's vision statement for creation
            products: Description of products for creation
            description: Company description for creation
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API for creation
            
        Returns:
            Dictionary with the default company details
            
        Raises:
            ValueError: If org_id is not provided, or if company_name is not provided and create_if_missing is True
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        try:
            # First, try to get the default company
            default_company = self.get_default(org_id=org_id)
            return default_company
        except Exception as e:
            error_msg = str(e)
            
            # If no default company exists and we're allowed to create one
            if create_if_missing:
                if not company_name:
                    raise ValueError("company_name is required when create_if_missing=True and no default company exists")
                    
                print(f"No default company found. Creating new company profile: {company_name}")
                
                # Create a new default company profile
                new_company = self.create(
                    company_name=company_name,
                    company_type=company_type,
                    tag_line=tag_line,
                    vision=vision,
                    products=products,
                    description=description,
                    is_default=True,
                    org_id=org_id,
                    **kwargs
                )
                return new_company
            else:
                # If we're not allowed to create one, re-raise the exception
                raise ValueError(f"No default company found and create_if_missing=False: {error_msg}")
