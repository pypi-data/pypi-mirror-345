import os
import json
import requests
from typing import Dict, List, Optional, Union, Any, Tuple, BinaryIO
import mimetypes
from urllib.parse import urljoin
import warnings
from .base_client import BaseClient

class StorageClient(BaseClient):
    """
    Client for interacting with Storylinez Storage API.
    Provides methods for managing files, folders, and storage resources.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the StorageClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.storage_url = f"{self.base_url}/storage"
        
        # Define allowed media formats
        self.allowed_formats = {
            'VIDEO': ['mp4'],
            'AUDIO': ['mp3', 'wav'], 
            'IMAGE': ['jpg', 'jpeg', 'png']
        }
    
    # Helper method to validate file extensions
    def _validate_file_extension(self, filename: str) -> str:
        """
        Validates that a file has an allowed extension.
        
        Args:
            filename: The filename to check
            
        Returns:
            The validated file extension without the dot
            
        Raises:
            ValueError: If the file extension is not allowed
        """
        extension = os.path.splitext(filename)[1].lower().lstrip('.')
        if not extension:
            raise ValueError(f"Filename '{filename}' has no extension")
            
        # Create a flat list of all allowed extensions
        all_allowed_extensions = []
        for formats in self.allowed_formats.values():
            all_allowed_extensions.extend(formats)
            
        if extension not in all_allowed_extensions:
            raise ValueError(f"File extension '{extension}' is not supported. Valid extensions are: {', '.join(all_allowed_extensions)}")
            
        return extension
    
    # Helper methods
    def _require_org_id(self, org_id: str = None) -> str:
        """Helper to require an org_id, using default if available"""
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        return org_id
    
    def _validate_path(self, path: str) -> str:
        """Ensure path starts with / and doesn't end with / unless it's the root"""
        if not path:
            return "/"
        if not path.startswith("/"):
            path = f"/{path}"
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        return path
    
    def _validate_file_exists(self, file_path: str) -> int:
        """Check if file exists and return its size"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
            
        # Validate file extension
        filename = os.path.basename(file_path)
        self._validate_file_extension(filename)
        
        return os.path.getsize(file_path)
    
    def _convert_bool_to_str(self, value: bool) -> str:
        """Convert boolean to lowercase string for API"""
        return str(value).lower()
    
    # File Upload Methods
    
    def generate_upload_link(self, 
                           filename: str, 
                           file_size: int = 0, 
                           folder_path: str = "/", 
                           org_id: str = None) -> Dict:
        """
        Generate a secure upload link for a file.
        
        Args:
            filename: Name of the file to upload
            file_size: Size of the file in bytes (optional, for quota check)
            folder_path: Target folder path (defaults to root)
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with upload details including:
            - upload_link: URL to upload the file to
            - key: S3 key for the file
            - upload_id: ID to reference this upload
            - expires_in: Expiration time in seconds
        
        Raises:
            ValueError: If filename is empty or org_id is not provided or file extension is not supported
        """
        org_id = self._require_org_id(org_id)
        
        if not filename or not filename.strip():
            raise ValueError("Filename is required")
            
        # Validate file extension
        self._validate_file_extension(filename)
        
        folder_path = self._validate_path(folder_path)
        
        params = {
            "org_id": org_id,
            "filename": filename,
            "file_size": file_size,
            "folder_path": folder_path
        }
        
        return self._make_request("GET", f"{self.storage_url}/upload/create_link", params=params)
    
    def upload_file(self, 
                  file_path: str, 
                  folder_path: str = "/", 
                  context: str = "", 
                  tags: List[str] = None,
                  analyze_audio: bool = True,
                  auto_company_details: bool = True,
                  company_details_id: str = "",
                  deepthink: bool = False,
                  overdrive: bool = False,
                  web_search: bool = False,
                  eco: bool = False,
                  temperature: float = 0.7,
                  org_id: str = None,
                  **kwargs) -> Dict:
        """
        Upload a file to Storylinez storage.
        This is a convenience method that handles both the link generation and upload.
        
        Args:
            file_path: Path to the file on local disk
            folder_path: Target folder path (defaults to root)
            context: Context for AI processing
            tags: Tags for categorization
            analyze_audio: Whether to analyze audio in media files
            auto_company_details: Whether to use company details for analysis
            company_details_id: ID of company details to use
            deepthink: Enable deep analysis
            overdrive: Use more computational resources
            web_search: Enable web search for analysis
            eco: Use eco-friendly processing
            temperature: AI temperature (0.0-1.0)
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters for backwards compatibility
        
        Returns:
            Dictionary with file details
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If temperature is out of range
            Exception: If upload fails
        """
        org_id = self._require_org_id(org_id)
            
        # Get file information and validate
        file_size = self._validate_file_exists(file_path)
        filename = os.path.basename(file_path)
        folder_path = self._validate_path(folder_path)
        
        # Validate temperature
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
            
        # Generate upload link
        upload_info = self.generate_upload_link(
            filename=filename,
            file_size=file_size,
            folder_path=folder_path,
            org_id=org_id
        )
        
        # Upload the file to the pre-signed URL
        upload_link = upload_info.get("upload_link")
        upload_id = upload_info.get("upload_id")
        
        if not upload_link or not upload_id:
            raise Exception("Failed to generate upload link")
        
        # Determine content type if not specified
        content_type = kwargs.get("content_type")
        if not content_type:
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Use requests to upload the file
        with open(file_path, 'rb') as file_data:
            headers = {'Content-Type': content_type}
            upload_response = requests.put(upload_link, data=file_data, headers=headers)
            
            if upload_response.status_code >= 400:
                raise Exception(f"File upload failed with status {upload_response.status_code}: {upload_response.text}")
        
        # Prepare completion data
        completion_data = {
            "org_id": org_id,
            "upload_id": upload_id,
            "filename": filename,
            "folder_path": folder_path,
            "context": context,
            "tags": tags or [],
            "analyze_audio": analyze_audio,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "web_search": web_search,
            "eco": eco,
            "temperature": temperature
        }
        
        # Additional parameters for backwards compatibility
        for key, value in kwargs.items():
            if key not in completion_data:
                completion_data[key] = value
        
        # Mark upload as complete and start processing
        return self._make_request("POST", f"{self.storage_url}/upload/complete", json_data=completion_data)
    
    def upload_file_data(self,
                       file_data: BinaryIO,
                       filename: str,
                       folder_path: str = "/",
                       content_type: str = None,
                       file_size: int = None,
                       context: str = "",
                       tags: List[str] = None,
                       analyze_audio: bool = True,
                       auto_company_details: bool = True,
                       company_details_id: str = "",
                       deepthink: bool = False,
                       overdrive: bool = False,
                       web_search: bool = False,
                       eco: bool = False,
                       temperature: float = 0.7,
                       org_id: str = None) -> Dict:
        """
        Upload file data directly from memory.
        
        Args:
            file_data: File-like object containing binary data
            filename: Name for the uploaded file
            folder_path: Target folder path (defaults to root)
            content_type: MIME type of the file (auto-detected if not provided)
            file_size: Size of data in bytes (will seek and calculate if None)
            context: Context for AI processing
            tags: Tags for categorization
            analyze_audio: Whether to analyze audio in media files
            auto_company_details: Whether to use company details for analysis
            company_details_id: ID of company details to use
            deepthink: Enable deep analysis
            overdrive: Use more computational resources
            web_search: Enable web search for analysis
            eco: Use eco-friendly processing
            temperature: AI temperature (0.0-1.0)
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with file details
            
        Raises:
            ValueError: For invalid parameters
            Exception: If upload fails
        """
        org_id = self._require_org_id(org_id)
        
        if not filename or not filename.strip():
            raise ValueError("Filename is required")
            
        # Validate file extension
        self._validate_file_extension(filename)
            
        # Determine file size if not provided
        if file_size is None:
            # Save current position
            current_pos = file_data.tell()
            # Seek to end to determine size
            file_data.seek(0, os.SEEK_END)
            file_size = file_data.tell()
            # Restore position
            file_data.seek(current_pos)
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
        # Validate temperature
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
            
        folder_path = self._validate_path(folder_path)
            
        # Generate upload link
        upload_info = self.generate_upload_link(
            filename=filename,
            file_size=file_size,
            folder_path=folder_path,
            org_id=org_id
        )
        
        # Upload the file to the pre-signed URL
        upload_link = upload_info.get("upload_link")
        upload_id = upload_info.get("upload_id")
        
        headers = {'Content-Type': content_type}
        upload_response = requests.put(upload_link, data=file_data, headers=headers)
        
        if upload_response.status_code >= 400:
            raise Exception(f"File upload failed with status {upload_response.status_code}: {upload_response.text}")
        
        # Prepare completion data
        completion_data = {
            "org_id": org_id,
            "upload_id": upload_id,
            "filename": filename,
            "mimetype": content_type,
            "folder_path": folder_path,
            "context": context,
            "tags": tags or [],
            "analyze_audio": analyze_audio,
            "auto_company_details": auto_company_details,
            "company_details_id": company_details_id,
            "deepthink": deepthink,
            "overdrive": overdrive,
            "web_search": web_search,
            "eco": eco,
            "temperature": temperature
        }
        
        # Mark upload as complete and start processing
        return self._make_request("POST", f"{self.storage_url}/upload/complete", json_data=completion_data)
    
    def mark_upload_complete(self, 
                           upload_id: str, 
                           org_id: str = None,
                           filename: str = None,
                           mimetype: str = None,
                           folder_path: str = None,
                           context: str = None,
                           tags: List[str] = None,
                           analyze_audio: bool = None,
                           auto_company_details: bool = None,
                           company_details_id: str = None,
                           deepthink: bool = None,
                           overdrive: bool = None,
                           web_search: bool = None,
                           eco: bool = None,
                           temperature: float = None,
                           **kwargs) -> Dict:
        """
        Mark an upload as complete after uploading to the pre-signed URL.
        
        Args:
            upload_id: The upload ID from generate_upload_link
            org_id: Organization ID (uses default if not provided)
            filename: Optional override for the filename
            mimetype: Optional MIME type for the file
            folder_path: Optional override for the folder path
            context: Optional context for AI processing
            tags: Optional tags for categorization
            analyze_audio: Whether to analyze audio in media files
            auto_company_details: Whether to use company details for analysis
            company_details_id: ID of company details to use
            deepthink: Enable deep analysis
            overdrive: Use more computational resources
            web_search: Enable web search for analysis
            eco: Use eco-friendly processing
            temperature: AI temperature (0.0-1.0)
            **kwargs: Additional parameters for backwards compatibility
        
        Returns:
            Dictionary with file details and job_id
            
        Raises:
            ValueError: For invalid parameters
        """
        org_id = self._require_org_id(org_id)
        
        if not upload_id:
            raise ValueError("Upload ID is required")
            
        data = {
            "org_id": org_id,
            "upload_id": upload_id
        }
        
        # Add other parameters if they were provided
        if filename:
            data["filename"] = filename
        
        if mimetype:
            data["mimetype"] = mimetype
            
        if folder_path:
            data["folder_path"] = self._validate_path(folder_path)
            
        if context is not None:
            data["context"] = context
            
        if tags is not None:
            data["tags"] = tags
            
        if analyze_audio is not None:
            data["analyze_audio"] = analyze_audio
            
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
            
        if temperature is not None:
            if not 0.0 <= temperature <= 1.0:
                raise ValueError("Temperature must be between 0.0 and 1.0")
            data["temperature"] = temperature
        
        # Additional parameters for backwards compatibility
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
        
        return self._make_request("POST", f"{self.storage_url}/upload/complete", json_data=data)
    
    # Folder Methods

    def get_folder_contents(self, 
                          path: str = "/", 
                          recursive: bool = False, 
                          detailed: bool = False, 
                          generate_thumbnail: bool = True,
                          generate_streamable: bool = False,
                          generate_download: bool = False,
                          include_protected: bool = False,
                          org_id: str = None) -> Dict:
        """
        Get the contents of a folder.
        
        Args:
            path: Folder path
            recursive: If True, include files from subfolders
            detailed: If True, include full analysis data
            generate_thumbnail: If True, generate thumbnail URLs
            generate_streamable: If True, generate streaming URLs
            generate_download: If True, generate download URLs
            include_protected: If True, include system-protected folders/files
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with folders and files lists
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        path = self._validate_path(path)
            
        params = {
            "org_id": org_id,
            "path": path,
            "recursive": self._convert_bool_to_str(recursive),
            "detailed": self._convert_bool_to_str(detailed),
            "generate_thumbnail": self._convert_bool_to_str(generate_thumbnail),
            "generate_streamable": self._convert_bool_to_str(generate_streamable),
            "generate_download": self._convert_bool_to_str(generate_download),
            "include_protected": self._convert_bool_to_str(include_protected)
        }
        
        return self._make_request("GET", f"{self.storage_url}/folder/contents", params=params)
    
    def create_folder(self, 
                    folder_name: str, 
                    parent_path: str = "/", 
                    org_id: str = None) -> Dict:
        """
        Create a new folder.
        
        Args:
            folder_name: Name of the folder to create
            parent_path: Path where the folder should be created
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with folder details
            
        Raises:
            ValueError: If folder_name contains '/' or org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        
        if not folder_name or not folder_name.strip():
            raise ValueError("Folder name is required")
            
        if '/' in folder_name:
            raise ValueError("Folder name cannot contain '/' character")
            
        parent_path = self._validate_path(parent_path)
            
        data = {
            "org_id": org_id,
            "folder_name": folder_name,
            "parent_path": parent_path
        }
        
        return self._make_request("POST", f"{self.storage_url}/folder/create", json_data=data)
    
    def delete_folder(self, 
                    folder_id: str, 
                    delete_contents: bool = False) -> Dict:
        """
        Delete a folder.
        
        Args:
            folder_id: ID of the folder to delete
            delete_contents: If True, delete all contents recursively
        
        Returns:
            Dictionary with deletion results
            
        Raises:
            ValueError: If folder_id is not provided
        """
        if not folder_id:
            raise ValueError("Folder ID is required")
            
        params = {
            "folder_id": folder_id,
            "delete_contents": self._convert_bool_to_str(delete_contents)
        }
        
        return self._make_request("DELETE", f"{self.storage_url}/folder/delete", params=params)
    
    def rename_folder(self, 
                    folder_id: str, 
                    new_name: str) -> Dict:
        """
        Rename a folder.
        
        Args:
            folder_id: ID of the folder to rename
            new_name: New name for the folder
        
        Returns:
            Dictionary with the updated folder details
            
        Raises:
            ValueError: If folder_id or new_name is not provided or if new_name contains '/'
        """
        if not folder_id:
            raise ValueError("Folder ID is required")
            
        if not new_name or not new_name.strip():
            raise ValueError("New folder name is required")
            
        if '/' in new_name:
            raise ValueError("Folder name cannot contain '/' character")
            
        data = {
            "folder_id": folder_id,
            "new_name": new_name
        }
        
        return self._make_request("PUT", f"{self.storage_url}/folder/rename", json_data=data)
    
    def get_folder_tree(self, 
                      path: str = "/", 
                      include_protected: bool = False,
                      org_id: str = None) -> Dict:
        """
        Get a hierarchical tree of folders and files.
        
        Args:
            path: Root path for the tree
            include_protected: If True, include system-protected folders/files
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with the tree structure
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        path = self._validate_path(path)
            
        params = {
            "org_id": org_id,
            "path": path,
            "include_protected": self._convert_bool_to_str(include_protected)
        }
        
        return self._make_request("GET", f"{self.storage_url}/tree", params=params)
    
    def list_folders(self, 
                   path: str = "/", 
                   recursive: bool = False, 
                   org_id: str = None) -> Dict:
        """
        List folders under a specific path.
        
        Args:
            path: Parent folder path
            recursive: If True, include all descendant folders
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with folders list
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        path = self._validate_path(path)
            
        params = {
            "org_id": org_id,
            "path": path,
            "recursive": self._convert_bool_to_str(recursive)
        }
        
        return self._make_request("GET", f"{self.storage_url}/folder/list", params=params)
    
    def search_files_by_name(self, 
                          query: str, 
                          path: str = "/", 
                          recursive: bool = False, 
                          detailed: bool = True,
                          generate_thumbnail: bool = True,
                          generate_streamable: bool = False,
                          generate_download: bool = False,
                          org_id: str = None) -> Dict:
        """
        Search for files by filename.
        
        Args:
            query: Text to search for in filenames
            path: Folder path to search within
            recursive: If True, search in subfolders
            detailed: If True, include full analysis data
            generate_thumbnail: If True, generate thumbnail URLs
            generate_streamable: If True, generate streamable URLs
            generate_download: If True, generate download URLs
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with matching files
            
        Raises:
            ValueError: If query is empty or org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        
        if not query or not query.strip():
            raise ValueError("Search query is required")
            
        path = self._validate_path(path)
            
        params = {
            "org_id": org_id,
            "path": path,
            "query": query,
            "recursive": self._convert_bool_to_str(recursive),
            "detailed": self._convert_bool_to_str(detailed),
            "generate_thumbnail": self._convert_bool_to_str(generate_thumbnail),
            "generate_streamable": self._convert_bool_to_str(generate_streamable),
            "generate_download": self._convert_bool_to_str(generate_download)
        }
        
        return self._make_request("GET", f"{self.storage_url}/folder/search-by-name", params=params)
    
    def vector_search(self, 
                    queries: List[str], 
                    path: str = None, 
                    detailed: bool = True, 
                    generate_thumbnail: bool = True,
                    generate_streamable: bool = False,
                    generate_download: bool = False,
                    num_results: int = 10, 
                    similarity_threshold: float = 0.5,
                    orientation: str = None,
                    file_types: str = "all",
                    org_id: str = None) -> Dict:
        """
        Search files semantically using vector embeddings.
        
        Args:
            queries: List of natural language queries
            path: Folder path to search within (None or empty to search all folders)
            detailed: If True, include full analysis data
            generate_thumbnail: If True, generate thumbnail URLs
            generate_streamable: If True, generate streamable URLs
            generate_download: If True, generate download URLs
            num_results: Maximum results per query (1-100)
            similarity_threshold: Minimum similarity score (0.0-1.0)
            orientation: Optional filter for video orientation ("landscape" or "portrait")
            file_types: Comma-separated list of types to search ("all", "video", "audio", "image")
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with semantically matching files
            
        Raises:
            ValueError: For invalid parameters
        """
        org_id = self._require_org_id(org_id)
        
        # Validate params
        if not queries:
            raise ValueError("At least one query is required")
            
        if not isinstance(queries, list):
            raise ValueError("queries must be a list of strings")
            
        if num_results < 1 or num_results > 100:
            raise ValueError("num_results must be between 1 and 100")
            
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
            
        if orientation and orientation not in ["landscape", "portrait"]:
            raise ValueError("orientation must be either 'landscape' or 'portrait'")
            
        valid_file_types = ["all", "video", "audio", "image"]
        if file_types:
            types = file_types.split(',')
            for t in types:
                if t.strip().lower() not in valid_file_types:
                    raise ValueError(f"Invalid file type '{t}'. Valid types are: {', '.join(valid_file_types)}")
        
        # Prepare path param - only add if explicitly provided
        params = {
            "org_id": org_id,
            "detailed": self._convert_bool_to_str(detailed),
            "generate_thumbnail": self._convert_bool_to_str(generate_thumbnail),
            "generate_streamable": self._convert_bool_to_str(generate_streamable),
            "generate_download": self._convert_bool_to_str(generate_download),
            "num_results": num_results,
            "similarity_threshold": similarity_threshold,
            "file_types": file_types
        }
        
        # Only add path if explicitly provided (to search all folders if None/empty)
        if path is not None and path != "":
            params["path"] = self._validate_path(path)
        else:
            # Let users know they're searching across ALL folders
            print("INFO: You're searching across ALL folders in the organization because no path was specified.")
            
        # Add orientation if provided
        if orientation:
            params["orientation"] = orientation
            
        data = {
            "queries": queries
        }
        
        return self._make_request("POST", f"{self.storage_url}/folder/vector-search", params=params, json_data=data)
    
    # File Methods
    
    def get_file_analysis(self, 
                        file_id: str, 
                        detailed: bool = True,
                        generate_thumbnail: bool = True,
                        generate_streamable: bool = True,
                        generate_download: bool = True) -> Dict:
        """
        Get detailed information about a file including analysis results.
        
        Args:
            file_id: File ID
            detailed: If True, include full analysis data
            generate_thumbnail: If True, generate thumbnail URL
            generate_streamable: If True, generate streaming URL
            generate_download: If True, generate download URL
        
        Returns:
            Dictionary with file details and analysis
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        params = {
            "file_id": file_id,
            "detailed": self._convert_bool_to_str(detailed),
            "generate_thumbnail": self._convert_bool_to_str(generate_thumbnail),
            "generate_streamable": self._convert_bool_to_str(generate_streamable),
            "generate_download": self._convert_bool_to_str(generate_download)
        }
        
        return self._make_request("GET", f"{self.storage_url}/file/analysis", params=params)
    
    def delete_file(self, file_id: str) -> Dict:
        """
        Delete a file.
        
        Args:
            file_id: ID of the file to delete
        
        Returns:
            Dictionary with deletion results
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        params = {
            "file_id": file_id
        }
        
        return self._make_request("DELETE", f"{self.storage_url}/file/delete", params=params)
    
    def rename_file(self, 
                  file_id: str, 
                  new_name: str) -> Dict:
        """
        Rename a file.
        
        Args:
            file_id: ID of the file to rename
            new_name: New name for the file
        
        Returns:
            Dictionary with the updated file details
            
        Raises:
            ValueError: If file_id or new_name is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        if not new_name or not new_name.strip():
            raise ValueError("New filename is required")
            
        data = {
            "file_id": file_id,
            "new_name": new_name
        }
        
        return self._make_request("PUT", f"{self.storage_url}/file/rename", json_data=data)
    
    def move_file(self, 
                file_id: str, 
                target_folder_path: str) -> Dict:
        """
        Move a file to a different folder.
        
        Args:
            file_id: ID of the file to move
            target_folder_path: Path of the target folder
        
        Returns:
            Dictionary with the updated file details
            
        Raises:
            ValueError: If file_id or target_folder_path is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        if target_folder_path is None:
            raise ValueError("Target folder path is required")
            
        target_folder_path = self._validate_path(target_folder_path)
            
        data = {
            "file_id": file_id,
            "target_folder_path": target_folder_path
        }
        
        return self._make_request("PUT", f"{self.storage_url}/file/move", json_data=data)
    
    def get_download_link(self, file_id: str) -> Dict:
        """
        Get a download link for a file (prioritizes processed version if available).
        
        Args:
            file_id: ID of the file
        
        Returns:
            Dictionary with download URL and expiration
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        params = {
            "file_id": file_id
        }
        
        return self._make_request("GET", f"{self.storage_url}/file/download", params=params)
    
    def get_original_download_link(self, file_id: str) -> Dict:
        """
        Get a download link specifically for the original unprocessed file.
        
        Args:
            file_id: ID of the file
        
        Returns:
            Dictionary with download URL and expiration
            
        Raises:
            ValueError: If file_id is not provided
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        params = {
            "file_id": file_id
        }
        
        return self._make_request("GET", f"{self.storage_url}/file/download/original", params=params)
    
    def reprocess_file(self, 
                     file_id: str,
                     context: str = None,
                     tags: List[str] = None,
                     analyze_audio: bool = None,
                     auto_company_details: bool = None,
                     company_details_id: str = None,
                     deepthink: bool = None,
                     overdrive: bool = None,
                     web_search: bool = None,
                     eco: bool = None,
                     temperature: float = None,
                     **kwargs) -> Dict:
        """
        Reprocess a file with new analysis parameters.
        
        Args:
            file_id: ID of the file to reprocess
            context: New context for AI processing
            tags: New tags for categorization
            analyze_audio: Whether to analyze audio in media files
            auto_company_details: Whether to use company details for analysis
            company_details_id: ID of company details to use
            deepthink: Enable deep analysis
            overdrive: Use more computational resources
            web_search: Enable web search for analysis
            eco: Use eco-friendly processing
            temperature: AI temperature (0.0-1.0)
            **kwargs: Additional parameters for backwards compatibility
        
        Returns:
            Dictionary with reprocessing details and new job_id
            
        Raises:
            ValueError: If file_id is not provided or parameters are invalid
        """
        if not file_id:
            raise ValueError("File ID is required")
            
        # Build request data with only provided parameters
        data = {}
            
        if context is not None:
            data["context"] = context
            
        if tags is not None:
            data["tags"] = tags
            
        if analyze_audio is not None:
            data["analyze_audio"] = analyze_audio
            
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
            
        if temperature is not None:
            if not 0.0 <= temperature <= 1.0:
                raise ValueError("Temperature must be between 0.0 and 1.0")
            data["temperature"] = temperature
            
        # Additional parameters for backwards compatibility
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
        
        return self._make_request("POST", f"{self.storage_url}/file/reprocess?file_id={file_id}", json_data=data)
    
    def get_files_by_ids(self, 
                       file_ids: List[str], 
                       detailed: bool = False, 
                       generate_thumbnail: bool = True,
                       generate_streamable: bool = False,
                       generate_download: bool = False,
                       org_id: str = None) -> Dict:
        """
        Get details for multiple files by their IDs.
        
        Args:
            file_ids: List of file IDs to retrieve
            detailed: If True, include full analysis data
            generate_thumbnail: If True, generate thumbnail URLs
            generate_streamable: If True, generate streamable URLs
            generate_download: If True, generate download URLs
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with file details for found files
            
        Raises:
            ValueError: If file_ids is empty or org_id is not provided
        """
        org_id = self._require_org_id(org_id)
        
        if not file_ids:
            raise ValueError("file_ids must be a non-empty list")
            
        if not isinstance(file_ids, list):
            raise ValueError("file_ids must be a list of strings")
            
        if len(file_ids) > 100:
            raise ValueError("Cannot request more than 100 files at once")
            
        params = {
            "org_id": org_id,
            "detailed": self._convert_bool_to_str(detailed),
            "generate_thumbnail": self._convert_bool_to_str(generate_thumbnail),
            "generate_streamable": self._convert_bool_to_str(generate_streamable),
            "generate_download": self._convert_bool_to_str(generate_download)
        }
        
        data = {
            "file_ids": file_ids
        }
        
        return self._make_request("POST", f"{self.storage_url}/files/get_by_ids", params=params, json_data=data)
    
    def get_storage_usage(self, org_id: str = None) -> Dict:
        """
        Get storage usage and limits for an organization.
        
        Args:
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with storage usage statistics
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = self._require_org_id(org_id)
            
        params = {
            "org_id": org_id
        }
        
        return self._make_request("GET", f"{self.storage_url}/storage/usage", params=params)

    # Advanced helper methods and workflows

    def ensure_folder_path(self, path: str, org_id: str = None) -> Dict:
        """
        Ensure a folder path exists, creating parent folders as needed.
        
        Args:
            path: The full folder path to ensure exists (e.g. "/path/to/folder")
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with the final folder details
            
        Raises:
            ValueError: If path is invalid
        """
        org_id = self._require_org_id(org_id)
        path = self._validate_path(path)
        
        # Root always exists
        if path == '/':
            return {'folder_id': 'root', 'path': '/', 'name': 'root'}
        
        # Split the path into parts
        parts = [p for p in path.split('/') if p]
        
        # Start from root
        current_path = '/'
        current_folder = {'folder_id': 'root', 'path': '/', 'name': 'root'}
        
        # Create each folder level if it doesn't exist
        for part in parts:
            next_path = f"{current_path}{part}" if current_path == '/' else f"{current_path}/{part}"
            
            # Check if folder exists
            folders_in_current = self.list_folders(current_path, recursive=False, org_id=org_id)
            
            # Find if this folder already exists
            found_folder = None
            for folder in folders_in_current.get('folders', []):
                if folder.get('path') == next_path:
                    found_folder = folder
                    break
            
            if found_folder:
                # Use existing folder
                current_folder = found_folder
            else:
                # Create new folder
                result = self.create_folder(part, current_path, org_id)
                current_folder = result.get('folder', {})
            
            # Update current path for next iteration
            current_path = next_path
        
        return current_folder
    
    def upload_directory(self, 
                       local_dir: str, 
                       remote_folder: str = "/", 
                       include_subdirs: bool = True,
                       file_extensions: List[str] = None,
                       context: str = "",
                       tags: List[str] = None,
                       analyze_audio: bool = True,
                       auto_company_details: bool = True,
                       org_id: str = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Upload all files from a local directory to a remote folder.
        
        Args:
            local_dir: Path to local directory
            remote_folder: Target remote folder path
            include_subdirs: If True, upload files in subdirectories maintaining structure
            file_extensions: List of file extensions to include (e.g. ['mp4', 'jpg'])
            context: Context for AI processing
            tags: Tags for categorization
            analyze_audio: Whether to analyze audio in media files
            auto_company_details: Whether to use company details for analysis
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters passed to upload_file
            
        Returns:
            Dictionary with upload results
            
        Raises:
            ValueError: If local_dir is not a directory
        """
        org_id = self._require_org_id(org_id)
        
        if not os.path.isdir(local_dir):
            raise ValueError(f"Not a directory: {local_dir}")
            
        remote_folder = self._validate_path(remote_folder)
        
        # Make sure the target folder exists
        self.ensure_folder_path(remote_folder, org_id)
        
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        # If file_extensions is provided, make sure they're all allowed
        if file_extensions:
            all_allowed_extensions = []
            for formats in self.allowed_formats.values():
                all_allowed_extensions.extend(formats)
                
            for ext in file_extensions:
                ext = ext.lower().lstrip('.')
                if ext not in all_allowed_extensions:
                    raise ValueError(f"Extension '{ext}' is not in the list of allowed extensions: {', '.join(all_allowed_extensions)}")
        
        # Walk through directory
        for root, dirs, files in os.walk(local_dir):
            if not include_subdirs and root != local_dir:
                # Skip subdirectories if not including them
                continue
                
            # Calculate relative path from local_dir
            rel_path = os.path.relpath(root, local_dir)
            if rel_path == '.':
                # We're in the root directory
                current_remote_folder = remote_folder
            else:
                # We're in a subdirectory - create remote path
                rel_path_parts = rel_path.replace('\\', '/').split('/')
                current_remote_folder = remote_folder + ('/' if remote_folder != '/' else '') + '/'.join(rel_path_parts)
                # Ensure this folder path exists
                self.ensure_folder_path(current_remote_folder, org_id)
            
            # Upload each file
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Check file extension if filter is provided
                if file_extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext.startswith('.'):
                        ext = ext[1:]  # Remove leading dot
                    
                    if ext not in file_extensions:
                        results["skipped"].append({
                            "path": file_path,
                            "reason": f"Extension '{ext}' not in allowed list"
                        })
                        continue
                
                try:
                    upload_result = self.upload_file(
                        file_path=file_path,
                        folder_path=current_remote_folder,
                        context=context,
                        tags=tags,
                        analyze_audio=analyze_audio,
                        auto_company_details=auto_company_details,
                        org_id=org_id,
                        **kwargs
                    )
                    
                    results["success"].append({
                        "local_path": file_path,
                        "remote_folder": current_remote_folder,
                        "file_id": upload_result.get("file", {}).get("file_id"),
                        "job_id": upload_result.get("job_id")
                    })
                    
                except Exception as e:
                    results["failed"].append({
                        "path": file_path,
                        "error": str(e)
                    })
        
        # Add counts to the results
        results["counts"] = {
            "success": len(results["success"]),
            "failed": len(results["failed"]),
            "skipped": len(results["skipped"]),
            "total": len(results["success"]) + len(results["failed"]) + len(results["skipped"])
        }
        
        return results
