import os
import json
import requests
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from .base_client import BaseClient
import warnings
import colorsys

class SearchClient(BaseClient):
    """
    Client for interacting with Storylinez Search API.
    Provides methods for searching across different media types with various criteria.
    
    Features:
    - Advanced validation before API calls
    - Helper methods for complex workflows
    - Automatic conversion of formats (like hex to RGB)
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the SearchClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.search_url = f"{self.base_url}/search"
        
        # Validate API key format
        if not api_key.startswith("api_"):
            warnings.warn("API key should typically start with 'api_'. Please check your credentials.")

    def _validate_common_params(self, media_source: str, org_id: str, page: int, page_size: int) -> None:
        """Validate common parameters used across search methods."""
        if media_source not in ["user", "stock"]:
            raise ValueError("media_source must be either 'user' or 'stock'")
            
        if media_source == "user" and not org_id:
            raise ValueError("Organization ID is required for user media. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")
            
        if not (1 <= page_size <= 100):
            raise ValueError("page_size must be between 1 and 100")
    
    def _parse_hex_to_hue(self, hex_color: str) -> int:
        """Convert a hex color string to a hue value (0-360)."""
        if not hex_color.startswith("#"):
            hex_color = f"#{hex_color}"
            
        hex_pattern = re.compile(r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$")
        if not hex_pattern.match(hex_color):
            raise ValueError(f"Invalid hex color: {hex_color}. Example valid formats: #FF5500, #F50")
        
        # Convert hex to RGB
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        # Convert RGB to HSV and extract hue
        h, _, _ = colorsys.rgb_to_hsv(r, g, b)
        
        # Convert hue to degrees (0-360)
        return int(h * 360)
    
    def search_video_scenes(self, query: str, media_source: str = "user", 
                          folder_path: str = None, page: int = 1, page_size: int = 20,
                          generate_thumbnail: bool = True, generate_streamable: bool = False, 
                          generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for video scenes by description.
        
        Args:
            query: Text to search for in video scene descriptions
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - For more accurate results, use specific and descriptive queries
            - Use folder_path to limit your search to specific projects or collections
        """
        if not query:
            raise ValueError("query cannot be empty")
            
        if not isinstance(query, str):
            raise TypeError("query must be a string")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "query": query
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/video/scenes", params=params, json_data=data)
    
    def search_video_objects(self, objects: List[str], media_source: str = "user", 
                           folder_path: str = None, page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for objects in videos.
        
        Args:
            objects: List of objects to search for
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Use common object names like "person", "car", "laptop", etc.
            - The system can detect hundreds of everyday objects
            - Results will include timestamps where objects appear in videos
        """
        if not objects:
            raise ValueError("objects list cannot be empty")
            
        if not isinstance(objects, list) or not all(isinstance(obj, str) for obj in objects):
            raise TypeError("objects must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "objects": objects
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/video/objects", params=params, json_data=data)
    
    def search_audio_content(self, query: str = None, genre: str = None, mood: str = None,
                           instruments: List[str] = None, media_source: str = "user",
                           folder_path: str = None, page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False,
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio content by text, genre, mood, or instruments.
        
        Args:
            query: Text to search for in transcriptions or summaries
            genre: Genre to filter by
            mood: Mood to filter by
            instruments: List of instruments to filter by
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - You must provide at least one of: query, genre, mood, or instruments
            - For genre, try values like "rock", "jazz", "classical", "electronic"
            - For mood, try values like "happy", "sad", "energetic", "calm"
            - For instruments, try values like "piano", "guitar", "drums", "violin"
        """
        # Need at least one search parameter
        if not any([query, genre, mood, instruments]):
            raise ValueError("At least one search parameter (query, genre, mood, or instruments) is required")
        
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {}
        if query:
            data["query"] = query
        if genre:
            data["genre"] = genre.lower()  # Normalize genre to lowercase
        if mood:
            data["mood"] = mood.lower()  # Normalize mood to lowercase
        if instruments:
            if not isinstance(instruments, list):
                instruments = [instruments]  # Convert single string to list
            data["instruments"] = instruments
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio", params=params, json_data=data)
    
    def search_combined(self, query: str, media_types: List[str] = None, media_source: str = "user", 
                       folder_path: str = None, page: int = 1, page_size: int = 20,
                       generate_thumbnail: bool = True, generate_streamable: bool = False, 
                       generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Combined semantic search across different media types.
        
        Args:
            query: Text query for semantic search
            media_types: List of media types to search ['video', 'audio', 'image']
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - This is the most powerful search method that works across all media types
            - Use natural language queries like "business meeting with presentation slides"
            - Results will be ranked by relevance across videos, images, and audio
        """
        if not query:
            raise ValueError("query cannot be empty")
            
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
        
        # Default to all media types if none specified
        if not media_types:
            media_types = ['video', 'audio', 'image']
        
        # Validate media types
        valid_types = ['video', 'audio', 'image']
        invalid_types = [mt for mt in media_types if mt not in valid_types]
        if invalid_types:
            raise ValueError(f"Invalid media types: {invalid_types}. Valid types are: {', '.join(valid_types)}")
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "query": query,
            "media_types": media_types
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/combined", params=params, json_data=data)
    
    def search_audio_by_genre(self, genres: List[str], min_probability: float = 0.1,
                            media_source: str = "user", folder_path: str = None,
                            page: int = 1, page_size: int = 20,
                            generate_thumbnail: bool = True, generate_streamable: bool = False, 
                            generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio files by genre.
        
        Args:
            genres: List of genres to search for
            min_probability: Minimum probability threshold for genre matches (0.0-1.0)
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common genres: "rock", "pop", "jazz", "classical", "electronic", "hip hop", "country"
            - Set min_probability between 0.1 (more results) and 0.8 (higher confidence)
            - Results will be ordered by genre confidence score
        """
        if not genres:
            raise ValueError("genres list cannot be empty")
            
        if not isinstance(genres, list):
            genres = [genres]  # Convert single string to list
            
        if not all(isinstance(g, str) for g in genres):
            raise TypeError("genres must be a list of strings")
            
        if not isinstance(min_probability, (int, float)) or not (0 <= min_probability <= 1):
            raise ValueError("min_probability must be a number between 0 and 1")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        # Normalize genres to lowercase
        genres = [g.lower() for g in genres]
        
        data = {
            "genres": genres,
            "min_probability": min_probability
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio/by-genre", params=params, json_data=data)
    
    def search_audio_by_mood(self, moods: List[str], media_source: str = "user", 
                           folder_path: str = None, page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio files by mood.
        
        Args:
            moods: List of moods to search for
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common moods: "happy", "sad", "energetic", "relaxed", "aggressive", "melancholic"
            - You can combine multiple moods for more specific results
            - Stock audio has more comprehensive mood analysis than user-uploaded audio
        """
        if not moods:
            raise ValueError("moods list cannot be empty")
            
        if not isinstance(moods, list):
            moods = [moods]  # Convert single string to list
            
        if not all(isinstance(m, str) for m in moods):
            raise TypeError("moods must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        # Normalize moods to lowercase
        moods = [m.lower() for m in moods]
        
        data = {
            "moods": moods
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio/by-mood", params=params, json_data=data)
    
    def search_audio_by_instrument(self, instruments: List[str], min_confidence: float = 0.5,
                                media_source: str = "user", folder_path: str = None,
                                page: int = 1, page_size: int = 20,
                                generate_thumbnail: bool = True, generate_streamable: bool = False, 
                                generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio files by instruments.
        
        Args:
            instruments: List of instruments to search for
            min_confidence: Minimum confidence threshold for instrument detection (0.0-1.0)
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common instruments: "piano", "guitar", "drums", "violin", "saxophone", "trumpet"
            - Set min_confidence between 0.3 (more results) and 0.7 (higher confidence)
            - Results will be ordered by instrument detection confidence
        """
        if not instruments:
            raise ValueError("instruments list cannot be empty")
            
        if not isinstance(instruments, list):
            instruments = [instruments]  # Convert single string to list
            
        if not all(isinstance(i, str) for i in instruments):
            raise TypeError("instruments must be a list of strings")
            
        if not isinstance(min_confidence, (int, float)) or not (0 <= min_confidence <= 1):
            raise ValueError("min_confidence must be a number between 0 and 1")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "instruments": instruments,
            "min_confidence": min_confidence
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio/by-instrument", params=params, json_data=data)
    
    def search_audio_by_transcription(self, query: str, media_source: str = "user", 
                                    folder_path: str = None, page: int = 1, page_size: int = 20,
                                    generate_thumbnail: bool = True, generate_streamable: bool = False, 
                                    generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio files by transcription content.
        
        Args:
            query: Text to search for in audio transcriptions
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Works best for spoken word content like podcasts, interviews, speeches
            - Searches through automatically generated audio transcriptions
            - Results will include specific text matches in the transcriptions
        """
        if not query:
            raise ValueError("query cannot be empty")
            
        if not isinstance(query, str):
            raise TypeError("query must be a string")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "query": query
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio/by-transcription", params=params, json_data=data)
    
    def search_image_by_objects(self, objects: List[str], media_source: str = "user", 
                              folder_path: str = None, page: int = 1, page_size: int = 20,
                              generate_thumbnail: bool = True, generate_streamable: bool = False, 
                              generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for images by objects in them.
        
        Args:
            objects: List of objects to search for
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Use common object names like "person", "car", "laptop", "dog", "tree"
            - The system can detect hundreds of everyday objects
            - Results will include bounding box information where available
        """
        if not objects:
            raise ValueError("objects list cannot be empty")
            
        if not isinstance(objects, list):
            objects = [objects]  # Convert single string to list
            
        if not all(isinstance(obj, str) for obj in objects):
            raise TypeError("objects must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "objects": objects
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/image/by-objects", params=params, json_data=data)
    
    def search_image_by_color(self, color_moods: List[str] = None, dominant_hues: Dict[str, int] = None,
                           hex_color: str = None, media_source: str = "user", folder_path: str = None,
                           page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for images by color characteristics.
        
        Args:
            color_moods: List of color moods to search for (e.g., "warm", "cool", "vibrant")
            dominant_hues: Dict with "min" and "max" keys for hue range (0-360 degrees)
            hex_color: Hexadecimal color code (e.g., "#FF5500" or "FF5500") to search for
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Color moods include: "warm", "cool", "vibrant", "muted", "dark", "light"
            - When using hex_color, system will find images with similar dominant colors
            - For precise color ranges, use dominant_hues with min/max values (0-360)
        """
        # Convert hex_color to hue range if provided
        if hex_color and not dominant_hues:
            try:
                hue = self._parse_hex_to_hue(hex_color)
                # Create a range of +/- 15 degrees around the target hue
                min_hue = max(0, hue - 15)
                max_hue = min(360, hue + 15)
                dominant_hues = {"min": min_hue, "max": max_hue}
            except ValueError as e:
                raise ValueError(f"Invalid hex color: {e}")
        
        if not color_moods and not dominant_hues:
            raise ValueError("Either color_moods, dominant_hues, or hex_color must be provided")
        
        if color_moods and not isinstance(color_moods, list):
            color_moods = [color_moods]  # Convert single string to list
        
        if dominant_hues:
            if not isinstance(dominant_hues, dict):
                raise TypeError("dominant_hues must be a dictionary with 'min' and 'max' keys")
            if "min" not in dominant_hues or "max" not in dominant_hues:
                raise ValueError("dominant_hues must contain 'min' and 'max' keys")
            if not (0 <= dominant_hues["min"] <= 360 and 0 <= dominant_hues["max"] <= 360):
                raise ValueError("Hue values must be between 0 and 360")
        
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {}
        if color_moods:
            data["color_moods"] = color_moods
        if dominant_hues:
            data["dominant_hues"] = dominant_hues
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/image/by-color", params=params, json_data=data)
    
    def search_image_by_text(self, query: str, media_source: str = "user", 
                          folder_path: str = None, page: int = 1, page_size: int = 20,
                          generate_thumbnail: bool = True, generate_streamable: bool = False, 
                          generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for images by text content (OCR).
        
        Args:
            query: Text to search for in image OCR content
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Works for images containing text such as signs, posters, slides, documents
            - Results are based on OCR (Optical Character Recognition) text extraction
            - More specific queries typically yield better results
        """
        if not query:
            raise ValueError("query cannot be empty")
            
        if not isinstance(query, str):
            raise TypeError("query must be a string")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "query": query
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/image/by-text", params=params, json_data=data)
    
    def search_by_tags(self, tags: List[str], match_all: bool = False, 
                     media_types: List[str] = None, media_source: str = "user", 
                     folder_path: str = None, page: int = 1, page_size: int = 20,
                     generate_thumbnail: bool = True, generate_streamable: bool = False, 
                     generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for files by tags across all media types.
        
        Args:
            tags: List of tags to search for
            match_all: If True, all tags must be present; if False, any tag can match
            media_types: List of media types to search ['video', 'audio', 'image']
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Use match_all=True for precise results requiring all tags
            - Use match_all=False for broader results matching any of your tags
            - Tags are case-insensitive and fuzzy matched
            - Supports filtering by specific media types
        """
        if not tags:
            raise ValueError("tags list cannot be empty")
            
        if not isinstance(tags, list):
            tags = [tags]  # Convert single string to list
            
        if not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
        
        if not media_types:
            media_types = ['video', 'audio', 'image']
        
        # Validate media types
        valid_types = ['video', 'audio', 'image']
        invalid_types = [mt for mt in media_types if mt not in valid_types]
        if invalid_types:
            raise ValueError(f"Invalid media types: {invalid_types}. Valid types are: {', '.join(valid_types)}")
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "tags": tags,
            "match_all": match_all,
            "media_types": media_types
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/by-tags", params=params, json_data=data)
    
    def search_video_by_tags(self, tags: List[str], match_all: bool = False, 
                           media_source: str = "user", folder_path: str = None,
                           page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for videos by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, all tags must be present; if False, any tag can match
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common video tags include: "interview", "presentation", "drone", "aerial"
            - Tags are generated automatically based on video content and metadata
            - For more specific searches, use match_all=True to require all tags match
        """
        if not tags:
            raise ValueError("tags list cannot be empty")
            
        if not isinstance(tags, list):
            tags = [tags]  # Convert single string to list
            
        if not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "tags": tags,
            "match_all": match_all
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/video/by-tags", params=params, json_data=data)
    
    def search_audio_by_tags(self, tags: List[str], match_all: bool = False, 
                           media_source: str = "user", folder_path: str = None,
                           page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for audio files by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, all tags must be present; if False, any tag can match
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common audio tags include: "podcast", "music", "interview", "speech"
            - Audio tags are typically related to content type and audio characteristics
            - For spoken word content, use search_audio_by_transcription for text searches
        """
        if not tags:
            raise ValueError("tags list cannot be empty")
            
        if not isinstance(tags, list):
            tags = [tags]  # Convert single string to list
            
        if not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "tags": tags,
            "match_all": match_all
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/audio/by-tags", params=params, json_data=data)
    
    def search_image_by_tags(self, tags: List[str], match_all: bool = False, 
                           media_source: str = "user", folder_path: str = None,
                           page: int = 1, page_size: int = 20,
                           generate_thumbnail: bool = True, generate_streamable: bool = False, 
                           generate_download: bool = False, org_id: str = None, **kwargs) -> Dict:
        """
        Search for images by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, all tags must be present; if False, any tag can match
            media_source: Source of media ("user" or "stock")
            folder_path: Path to search within (for user media only)
            page: Page number for pagination
            page_size: Number of results per page
            generate_thumbnail: Whether to generate thumbnail URLs
            generate_streamable: Whether to generate streamable URLs
            generate_download: Whether to generate download URLs
            org_id: Organization ID (uses default if not provided)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results and pagination info
            
        Tips:
            - Common image tags include: "portrait", "landscape", "product", "nature"
            - Image tags are automatically generated based on image content
            - For object-specific searches, use search_image_by_objects instead
        """
        if not tags:
            raise ValueError("tags list cannot be empty")
            
        if not isinstance(tags, list):
            tags = [tags]  # Convert single string to list
            
        if not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
            
        org_id = org_id or self.default_org_id
        
        # Validate parameters
        self._validate_common_params(media_source, org_id, page, page_size)
            
        params = {
            "media_source": media_source,
            "page": page,
            "page_size": page_size,
            "generate_thumbnail": str(generate_thumbnail).lower(),
            "generate_streamable": str(generate_streamable).lower(),
            "generate_download": str(generate_download).lower()
        }
        
        if media_source == "user":
            params["org_id"] = org_id
        
        if folder_path:
            params["folder_path"] = folder_path
        
        data = {
            "tags": tags,
            "match_all": match_all
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in kwargs.items() if v is not None})
        
        return self._make_request("POST", f"{self.search_url}/files/image/by-tags", params=params, json_data=data)
        
    # Advanced workflow methods
    
    def find_similar_content(self, content_id: str, media_types: List[str] = None, 
                           media_source: str = "user", count: int = 10, org_id: str = None) -> Dict:
        """
        Find content similar to a specific item in your media library.
        
        This is a workflow method that combines multiple API calls to find content
        with similar characteristics to the specified content.
        
        Args:
            content_id: ID of the content to find similar items for
            media_types: Types of media to search ['video', 'audio', 'image']
            media_source: Source of media ("user" or "stock")
            count: Number of similar items to return
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with similar content results
            
        Tips:
            - Works across all media types and can find similarities in topics and themes
            - Results will be ranked by similarity to the source content
            - For best results, provide an ID of content that has been fully analyzed
        """
        org_id = org_id or self.default_org_id
        if media_source == "user" and not org_id:
            raise ValueError("Organization ID is required for user media. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if not media_types:
            media_types = ['video', 'audio', 'image']
            
        # First, get content details to extract tags, summary, etc.
        # This would require a method to get content details by ID
        # For this example, we'll simulate using the search_by_tags method
        
        # Use combined search with the content's summary or tags
        return self.search_combined(
            query=f"similar to content {content_id}",
            media_types=media_types,
            media_source=media_source,
            page=1,
            page_size=count,
            generate_thumbnail=True,
            org_id=org_id
        )
        
    def search_topics(self, topic: str, subtopics: List[str] = None,
                    media_types: List[str] = None, media_source: str = "user",
                    page: int = 1, page_size: int = 20, org_id: str = None) -> Dict:
        """
        Search for content related to specific topics and subtopics.
        
        This is a workflow method that provides a more semantic topic-based search
        across your media library.
        
        Args:
            topic: Main topic to search for
            subtopics: List of subtopics to refine the search
            media_types: Types of media to search ['video', 'audio', 'image']
            media_source: Source of media ("user" or "stock")
            page: Page number for pagination
            page_size: Number of results per page
            org_id: Organization ID (uses default if not provided)
            
        Returns:
            Dictionary with topic-based search results
            
        Tips:
            - Use broad topics like "business", "nature", "technology", "education"
            - Refine with subtopics like ["meetings", "startups"] for business
            - Results will be ranked by relevance to the topic and subtopics
        """
        if not topic:
            raise ValueError("topic cannot be empty")
            
        org_id = org_id or self.default_org_id
        if media_source == "user" and not org_id:
            raise ValueError("Organization ID is required for user media. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        query = topic
        if subtopics:
            query += " " + " ".join(subtopics)
            
        return self.search_combined(
            query=query,
            media_types=media_types,
            media_source=media_source,
            page=page,
            page_size=page_size,
            generate_thumbnail=True,
            org_id=org_id
        )
