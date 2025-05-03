import os
import json
import requests
import warnings
from typing import Dict, List, Optional, Union, Any, Tuple
from .base_client import BaseClient

class StockClient(BaseClient):
    """
    Client for interacting with Storylinez Stock Media API.
    Provides methods for searching and fetching stock videos, audios, and images.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the StockClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.stock_url = f"{self.base_url}/stock"
    
    def search(self, queries: List[str], collections: List[str] = None, 
              detailed: bool = False, generate_thumbnail: bool = False,
              generate_streamable: bool = False, generate_download: bool = False,
              num_results: int = None, num_results_videos: int = 1, 
              num_results_audios: int = 1, num_results_images: int = 1,
              similarity_threshold: float = 0.5, orientation: str = None,
              **kwargs) -> Dict:
        """
        Search for stock media items across videos, audios, and/or images collections using semantic search.
        
        Args:
            queries: List of natural language search queries
            collections: List of collections to search ('videos', 'audios', 'images'). Defaults to all.
            detailed: Whether to include full analysis data in results
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable media URLs
            generate_download: Whether to generate download URLs
            num_results: Override for max results per collection (overrides individual settings)
            num_results_videos: Maximum number of video results per query
            num_results_audios: Maximum number of audio results per query
            num_results_images: Maximum number of image results per query
            similarity_threshold: Minimum similarity score (0.0-1.0)
            orientation: Filter videos by orientation ('landscape' or 'portrait')
            
        Returns:
            Dictionary containing search results grouped by media type
        """
        # Input validation
        if not queries:
            raise ValueError("At least one query is required")
        
        if not isinstance(queries, list):
            raise TypeError("queries must be a list of strings")
            
        # Check if queries are all strings
        if not all(isinstance(q, str) for q in queries):
            raise ValueError("All queries must be strings")
            
        # Validate collections
        valid_collections = ['videos', 'audios', 'images']
        if collections:
            if not isinstance(collections, list):
                raise TypeError("collections must be a list of strings")
                
            invalid_collections = [c for c in collections if c not in valid_collections]
            if invalid_collections:
                raise ValueError(f"Invalid collection(s): {', '.join(invalid_collections)}. Valid values are: {', '.join(valid_collections)}")
        
        # Validate similarity_threshold
        if similarity_threshold < 0 or similarity_threshold > 1:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
            
        # Validate orientation
        if orientation and orientation not in ['landscape', 'portrait']:
            raise ValueError("orientation must be either 'landscape' or 'portrait'")
            
        if orientation and (not collections or 'videos' not in collections):
            warnings.warn("Orientation filter only applies to videos and will be ignored for other media types")
            
        # Build query parameters
        params = {
            "detailed": str(detailed).lower(),
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower(),
            "similarity_threshold": similarity_threshold,
        }
        
        # Add optional parameters
        if collections:
            for collection in collections:
                params["collections"] = collection
                
        if num_results is not None:
            params["num_results"] = num_results
        else:
            params["num_results_videos"] = num_results_videos
            params["num_results_audios"] = num_results_audios
            params["num_results_images"] = num_results_images
            
        if orientation:
            params["orientation"] = orientation
        
        # Add any additional parameters from kwargs (for backward compatibility)
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Send search request
        data = {
            "queries": queries
        }
        
        return self._make_request("POST", f"{self.stock_url}/search", params=params, json_data=data)
    
    def get_by_id(self, stock_id: str, media_type: str, detailed: bool = True,
                 generate_thumbnail: bool = True, generate_streamable: bool = False,
                 generate_download: bool = False, **kwargs) -> Dict:
        """
        Get a specific stock media item by ID.
        
        Args:
            stock_id: ID of the stock item to retrieve
            media_type: Type of media ('videos', 'audios', or 'images')
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URL
            generate_streamable: Whether to generate streamable media URL
            generate_download: Whether to generate download URL
            
        Returns:
            Dictionary containing the stock item details
        """
        # Input validation
        if not stock_id:
            raise ValueError("stock_id is required")
            
        # Validate media_type
        valid_media_types = ['videos', 'audios', 'images']
        if media_type not in valid_media_types:
            raise ValueError(f"media_type must be one of: {', '.join(valid_media_types)}")
            
        params = {
            "id": stock_id,
            "media_type": media_type,
            "detailed": str(detailed).lower(),
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        # Add any additional parameters from kwargs (for backward compatibility)
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("GET", f"{self.stock_url}/get_by_id", params=params)
    
    def list_media(self, media_type: str, page: int = 1, limit: int = 20, 
                 sort_by: str = "processed_at", sort_order: str = "desc",
                 detailed: bool = False, generate_thumbnail: bool = False,
                 generate_streamable: bool = False, generate_download: bool = False,
                 orientation: str = None, search: str = None, **kwargs) -> Dict:
        """
        List stock media items with pagination.
        
        Args:
            media_type: Type of media to list ('videos', 'audios', or 'images')
            page: Page number for pagination (starting from 1)
            limit: Maximum number of items per page (max 100)
            sort_by: Field to sort by (e.g., 'processed_at')
            sort_order: Sort direction ('asc' or 'desc')
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable media URLs
            generate_download: Whether to generate download URLs
            orientation: Filter videos by orientation ('landscape' or 'portrait')
            search: Optional text search within title/metadata
            
        Returns:
            Dictionary containing paginated media items and pagination info
        """
        # Input validation
        valid_media_types = ['videos', 'audios', 'images']
        if media_type not in valid_media_types:
            raise ValueError(f"media_type must be one of: {', '.join(valid_media_types)}")
            
        # Validate sort_order
        if sort_order not in ['asc', 'desc']:
            raise ValueError("sort_order must be either 'asc' or 'desc'")
            
        # Validate orientation if provided
        if orientation:
            if orientation not in ['landscape', 'portrait']:
                raise ValueError("orientation must be either 'landscape' or 'portrait'")
            if media_type != 'videos':
                warnings.warn("orientation filter only applies to videos and will be ignored")
        
        # Validate page and limit
        if page < 1:
            raise ValueError("page must be at least 1")
            
        if limit < 1:
            raise ValueError("limit must be at least 1")
            
        if limit > 100:
            warnings.warn(f"limit capped at 100 (requested: {limit})")
            limit = min(limit, 100)
        
        params = {
            "media_type": media_type,
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "detailed": str(detailed).lower(),
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        # Add optional parameters
        if orientation:
            params["orientation"] = orientation
            
        if search:
            params["search"] = search
            
        # Add any additional parameters from kwargs (for backward compatibility)
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("GET", f"{self.stock_url}/list", params=params)
    
    def get_by_ids(self, ids: List[str], media_types: List[str], 
                  detailed: bool = True, generate_thumbnail: bool = True,
                  generate_streamable: bool = False, generate_download: bool = False,
                  **kwargs) -> Dict:
        """
        Get multiple stock media items by their IDs.
        
        Args:
            ids: List of stock item IDs
            media_types: Corresponding media types for each ID ('videos', 'audios', 'images')
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable media URLs
            generate_download: Whether to generate download URLs
            
        Returns:
            Dictionary containing the requested stock items
        """
        # Input validation
        if not ids:
            raise ValueError("ids list cannot be empty")
            
        if not media_types:
            raise ValueError("media_types list cannot be empty")
            
        if len(ids) != len(media_types):
            raise ValueError("The ids and media_types lists must be the same length")
            
        if len(ids) > 100:
            raise ValueError("Cannot request more than 100 items at once")
            
        # Validate media types
        valid_media_types = ['videos', 'audios', 'images']
        invalid_types = [mt for mt in media_types if mt not in valid_media_types]
        if invalid_types:
            raise ValueError(f"Invalid media type(s): {', '.join(set(invalid_types))}. Valid values are: {', '.join(valid_media_types)}")
        
        params = {
            "detailed": str(detailed).lower(),
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        # Add any additional parameters from kwargs (for backward compatibility)
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        data = {
            "ids": ids,
            "media_types": media_types
        }
        
        return self._make_request("POST", f"{self.stock_url}/get_by_ids", params=params, json_data=data)
    
    # Utility methods for common workflows
    
    def search_videos(self, query: str, num_results: int = 5, orientation: str = None, 
                     detailed: bool = False, generate_thumbnail: bool = True,
                     generate_streamable: bool = True) -> List[Dict]:
        """
        Convenience method to search only for videos.
        
        Args:
            query: Natural language search query
            num_results: Maximum number of results to return
            orientation: Filter by orientation ('landscape' or 'portrait')
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable media URLs
            
        Returns:
            List of video results
        """
        results = self.search(
            queries=[query],
            collections=['videos'],
            detailed=detailed,
            generate_thumbnail=generate_thumbnail,
            generate_streamable=generate_streamable,
            num_results_videos=num_results,
            orientation=orientation
        )
        
        return results.get('videos', [])
    
    def search_audios(self, query: str, num_results: int = 5, 
                     detailed: bool = False, generate_thumbnail: bool = True,
                     generate_streamable: bool = True) -> List[Dict]:
        """
        Convenience method to search only for audio.
        
        Args:
            query: Natural language search query
            num_results: Maximum number of results to return
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable media URLs
            
        Returns:
            List of audio results
        """
        results = self.search(
            queries=[query],
            collections=['audios'],
            detailed=detailed,
            generate_thumbnail=generate_thumbnail,
            generate_streamable=generate_streamable,
            num_results_audios=num_results
        )
        
        return results.get('audios', [])
    
    def search_images(self, query: str, num_results: int = 5, 
                     detailed: bool = False, generate_thumbnail: bool = True) -> List[Dict]:
        """
        Convenience method to search only for images.
        
        Args:
            query: Natural language search query
            num_results: Maximum number of results to return
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            
        Returns:
            List of image results
        """
        results = self.search(
            queries=[query],
            collections=['images'],
            detailed=detailed,
            generate_thumbnail=generate_thumbnail,
            num_results_images=num_results
        )
        
        return results.get('images', [])
    
    def find_similar_media(self, stock_id: str, media_type: str, num_results: int = 5) -> Dict:
        """
        Find media similar to a specific stock item.
        
        This is a higher-level workflow that:
        1. Gets the specified item's detailed data
        2. Uses its description to search for similar items
        
        Args:
            stock_id: ID of the reference stock item
            media_type: Type of the reference media ('videos', 'audios', or 'images')
            num_results: Number of similar items to find per media type
            
        Returns:
            Dictionary containing search results grouped by media type
        """
        # Get the reference item
        item = self.get_by_id(stock_id=stock_id, media_type=media_type, detailed=True)
        
        # Extract description from analysis results
        description = ""
        if 'analysis_data' in item and 'results' in item['analysis_data']:
            results = item['analysis_data']['results']
            description = results.get('summary', '') or results.get('description', '')
            
        if not description:
            # Fallback to original metadata
            if 'original_metadata' in item:
                description = item['original_metadata'].get('description', '')
                
        if not description:
            raise ValueError("Could not extract description from the reference item")
            
        # Search for similar media using the description
        return self.search(
            queries=[description],
            detailed=False,
            generate_thumbnail=True,
            num_results_videos=num_results,
            num_results_audios=num_results,
            num_results_images=num_results
        )
    
    def batch_get_items(self, ids_by_media_type: Dict[str, List[str]],
                       detailed: bool = True, generate_thumbnail: bool = True) -> Dict[str, List[Dict]]:
        """
        Batch fetch items by media type.
        
        Args:
            ids_by_media_type: Dictionary mapping media types to lists of IDs.
              Example: {'videos': ['id1', 'id2'], 'images': ['id3', 'id4']}
            detailed: Whether to include full analysis data
            generate_thumbnail: Whether to generate thumbnail URLs
            
        Returns:
            Dictionary of items grouped by media type
        """
        # Validate input
        valid_media_types = ['videos', 'audios', 'images']
        for media_type in ids_by_media_type:
            if media_type not in valid_media_types:
                raise ValueError(f"Invalid media type: {media_type}. Valid values are: {', '.join(valid_media_types)}")
        
        # Flatten IDs and media types for the API call
        flat_ids = []
        flat_media_types = []
        
        for media_type, ids in ids_by_media_type.items():
            flat_ids.extend(ids)
            flat_media_types.extend([media_type] * len(ids))
            
        if not flat_ids:
            return {'videos': [], 'audios': [], 'images': []}
            
        # Call the API
        result = self.get_by_ids(
            ids=flat_ids,
            media_types=flat_media_types,
            detailed=detailed,
            generate_thumbnail=generate_thumbnail
        )
        
        # Reorganize results by media type
        items_by_type = {'videos': [], 'audios': [], 'images': []}
        
        for item in result.get('items', []):
            media_type = item.get('media_type')
            if media_type in items_by_type:
                items_by_type[media_type].append(item)
                
        return items_by_type
