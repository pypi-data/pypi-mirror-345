import os
import json
import requests
from typing import Dict, List, Optional, Union, Any, Tuple, TypeVar, cast
from datetime import datetime
from .base_client import BaseClient
import re
import warnings
import time

# Type alias for RGB colors
RGB = Tuple[int, int, int]
# Type alias for RGBA colors
RGBA = Tuple[int, int, int, int]
# Type for either RGB or RGBA
ColorType = TypeVar('ColorType', RGB, RGBA)

class RenderClient(BaseClient):
    """
    Client for interacting with Storylinez Render API.
    Provides methods for creating and managing video renders based on sequences.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the RenderClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.render_url = f"{self.base_url}/render"
    
    # Utility functions for parameter handling
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> RGB:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return (int(hex_color[0:2], 16), 
                int(hex_color[2:4], 16), 
                int(hex_color[4:6], 16))
    
    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> RGBA:
        """Convert hex color string to RGBA tuple with specified alpha"""
        rgb = RenderClient._hex_to_rgb(hex_color)
        return (rgb[0], rgb[1], rgb[2], min(255, max(0, int(alpha * 255))))
    
    @staticmethod
    def _normalize_color(color: Union[str, List[int], Tuple[int, ...]], include_alpha: bool = False) -> Union[RGB, RGBA]:
        """
        Normalize a color value to RGB or RGBA tuple
        
        Args:
            color: Color in hex string format or RGB(A) list/tuple
            include_alpha: Whether to include alpha channel (defaults to False)
            
        Returns:
            RGB or RGBA tuple
        """
        if isinstance(color, str):
            # Handle hex color strings
            if color.startswith('#') or re.match(r'^[0-9a-fA-F]{6}$', color):
                rgb = RenderClient._hex_to_rgb(color)
                if include_alpha:
                    return (rgb[0], rgb[1], rgb[2], 255)  # Full opacity
                return rgb
            else:
                raise ValueError(f"Invalid hex color format: {color}")
        elif isinstance(color, (list, tuple)):
            # Handle RGB(A) lists/tuples
            if include_alpha:
                if len(color) == 3:
                    return (color[0], color[1], color[2], 255)  # Add full opacity
                elif len(color) == 4:
                    return (color[0], color[1], color[2], color[3])
                else:
                    raise ValueError(f"Color must have 3 or 4 components: {color}")
            else:
                if len(color) >= 3:
                    return (color[0], color[1], color[2])  # Take only RGB components
                else:
                    raise ValueError(f"Color must have at least 3 components: {color}")
        else:
            raise TypeError(f"Color must be a hex string or RGB(A) list/tuple: {color}")
    
    @staticmethod
    def _validate_volume(volume: float) -> float:
        """
        Validate and normalize a volume value
        
        Args:
            volume: Volume value (should be between 0.0 and 1.0)
            
        Returns:
            Normalized volume value
        """
        try:
            volume = float(volume)
            if volume < 0.0:
                warnings.warn(f"Volume {volume} is negative, clamping to 0.0")
                return 0.0
            if volume > 1.2:
                warnings.warn(f"Volume {volume} exceeds 1.2, which may cause distortion. Values between 0.0 and 1.0 are recommended.")
            return volume
        except (ValueError, TypeError):
            raise ValueError(f"Volume must be a number between 0.0 and 1.0: {volume}")
    
    @staticmethod
    def _validate_dimensions(width: int, height: int, orientation: str) -> bool:
        """
        Validate video dimensions based on orientation
        
        Args:
            width: Video width in pixels
            height: Video height in pixels
            orientation: 'landscape' or 'portrait'
            
        Returns:
            True if dimensions are valid, False otherwise
        """
        # Minimum and maximum resolution limits
        MIN_WIDTH = 640
        MIN_HEIGHT = 360
        MAX_WIDTH = 7680
        MAX_HEIGHT = 4320
        
        # Check minimum resolution
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            raise ValueError(f"Resolution too small. Minimum dimensions: {MIN_WIDTH}x{MIN_HEIGHT}")
            
        # Check maximum resolution
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValueError(f"Resolution too large. Maximum dimensions: {MAX_WIDTH}x{MAX_HEIGHT}")
            
        # Aspect ratio validation
        if orientation == 'landscape' and width <= height:
            raise ValueError("For landscape orientation, width must be greater than height")
        elif orientation == 'portrait' and height <= width:
            raise ValueError("For portrait orientation, height must be greater than width")
            
        return True
    
    # Render Creation and Management
    
    def create_render(
        self, 
        project_id: str,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        bg_music_volume: Optional[float] = None,
        video_audio_volume: Optional[float] = None,
        voiceover_volume: Optional[float] = None,
        subtitle_enabled: Optional[bool] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_color: Optional[Union[str, List[int], Tuple[int, ...]]] = None,
        subtitle_bg_color: Optional[Union[str, List[int], Tuple[int, ...]]] = None,
        subtitle_bg_opacity: Optional[float] = None,
        outro_duration: Optional[float] = None,
        company_name: Optional[str] = None,
        company_subtext: Optional[str] = None,
        call_to_action: Optional[str] = None,
        call_to_action_subtext: Optional[str] = None,
        enable_cta: Optional[bool] = None,
        color_balance_fix: Optional[bool] = None,
        color_exposure_fix: Optional[bool] = None,
        color_contrast_fix: Optional[bool] = None,
        extend_short_clips: Optional[bool] = None,
        extension_method: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Create a new render for a project. The project must have an existing sequence.
        
        Args:
            project_id: ID of the project to create the render for
            target_width: Width of the output video (must be valid for orientation)
            target_height: Height of the output video (must be valid for orientation)
            bg_music_volume: Background music volume (0.0 to 1.0)
            video_audio_volume: Video audio track volume (0.0 to 1.0)
            voiceover_volume: Voiceover track volume (0.0 to 1.0)
            subtitle_enabled: Whether to show subtitles
            subtitle_font_size: Subtitle text size
            subtitle_color: Subtitle text color (RGB tuple/list or hex string)
            subtitle_bg_color: Subtitle background color (RGB tuple/list or hex string)
            subtitle_bg_opacity: Subtitle background opacity (0.0 to 1.0)
            outro_duration: Duration of the outro in seconds
            company_name: Company name to display in outro
            company_subtext: Company tagline to display in outro
            call_to_action: CTA text
            call_to_action_subtext: CTA subtext
            enable_cta: Whether to show CTA
            color_balance_fix: Apply color balance correction
            color_exposure_fix: Apply exposure correction
            color_contrast_fix: Apply contrast correction
            extend_short_clips: Automatically extend clips shorter than the minimum duration
            extension_method: Method to extend short clips ('freeze', 'loop', or 'mirror')
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with the created render details and job information
        """
        if not project_id:
            raise ValueError("project_id is required")
            
        data = {"project_id": project_id}
        
        # Process specific parameters with validation
        if target_width is not None:
            data["target_width"] = int(target_width)
        
        if target_height is not None:
            data["target_height"] = int(target_height)
            
        # Volume parameters
        if bg_music_volume is not None:
            data["bg_music_volume"] = self._validate_volume(bg_music_volume)
            
        if video_audio_volume is not None:
            data["video_audio_volume"] = self._validate_volume(video_audio_volume)
            
        if voiceover_volume is not None:
            data["voiceover_volume"] = self._validate_volume(voiceover_volume)
        
        # Boolean parameters
        for param_name, param_value in [
            ("subtitle_enabled", subtitle_enabled),
            ("enable_cta", enable_cta),
            ("color_balance_fix", color_balance_fix),
            ("color_exposure_fix", color_exposure_fix),
            ("color_contrast_fix", color_contrast_fix),
            ("extend_short_clips", extend_short_clips)
        ]:
            if param_value is not None:
                data[param_name] = bool(param_value)
        
        # Color parameters
        if subtitle_color is not None:
            data["subtitle_color"] = self._normalize_color(subtitle_color)
            
        if subtitle_bg_color is not None:
            data["subtitle_bg_color"] = self._normalize_color(subtitle_bg_color)
        
        # Other numeric parameters
        if subtitle_font_size is not None:
            data["subtitle_font_size"] = int(subtitle_font_size)
            
        if subtitle_bg_opacity is not None:
            if not 0.0 <= subtitle_bg_opacity <= 1.0:
                warnings.warn(f"subtitle_bg_opacity should be between 0.0 and 1.0, got {subtitle_bg_opacity}")
            data["subtitle_bg_opacity"] = float(subtitle_bg_opacity)
            
        if outro_duration is not None:
            if outro_duration < 0:
                raise ValueError("outro_duration cannot be negative")
            data["outro_duration"] = float(outro_duration)
        
        # String parameters
        for param_name, param_value in [
            ("company_name", company_name),
            ("company_subtext", company_subtext),
            ("call_to_action", call_to_action),
            ("call_to_action_subtext", call_to_action_subtext),
            ("extension_method", extension_method)
        ]:
            if param_value is not None:
                data[param_name] = str(param_value)
                
        # Validate extension method
        if extension_method is not None and extension_method not in ["freeze", "loop", "mirror"]:
            raise ValueError("extension_method must be 'freeze', 'loop', or 'mirror'")
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            data[key] = value
        
        return self._make_request("POST", f"{self.render_url}/create", json_data=data)
    
    def get_render(
        self, 
        render_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        include_results: bool = True, 
        include_sequence: bool = False,
        include_subtitles: bool = False, 
        generate_download_link: bool = False,
        generate_streamable_link: bool = False, 
        generate_thumbnail_stream_link: bool = False
    ) -> Dict:
        """
        Get details of a render by either render ID or project ID.
        
        Args:
            render_id: ID of the render to retrieve (either this or project_id must be provided)
            project_id: ID of the project to retrieve the render for (either this or render_id must be provided)
            include_results: Whether to include job results
            include_sequence: Whether to include the full sequence data
            include_subtitles: Whether to include subtitles data
            generate_download_link: Whether to generate a temporary download link
            generate_streamable_link: Whether to generate a temporary streamable link
            generate_thumbnail_stream_link: Whether to generate a thumbnail streamable link
            
        Returns:
            Dictionary with render details
        """
        if not render_id and not project_id:
            raise ValueError("Either render_id or project_id must be provided")
            
        params = {
            "include_results": str(include_results).lower(),
            "include_sequence": str(include_sequence).lower(),
            "include_subtitles": str(include_subtitles).lower(),
            "generate_download_link": str(generate_download_link).lower(),
            "generate_streamable_link": str(generate_streamable_link).lower(),
            "generate_thumbnail_stream_link": str(generate_thumbnail_stream_link).lower()
        }
        
        if render_id:
            params["render_id"] = render_id
        if project_id:
            params["project_id"] = project_id
            
        return self._make_request("GET", f"{self.render_url}/get", params=params)
    
    def redo_render(
        self, 
        render_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        bg_music_volume: Optional[float] = None,
        video_audio_volume: Optional[float] = None,
        voiceover_volume: Optional[float] = None,
        subtitle_enabled: Optional[bool] = None,
        color_balance_fix: Optional[bool] = None,
        color_exposure_fix: Optional[bool] = None,
        color_contrast_fix: Optional[bool] = None,
        extend_short_clips: Optional[bool] = None,
        extension_method: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Regenerate a render with the same or updated settings.
        
        Args:
            render_id: ID of the render to regenerate (either this or project_id must be provided)
            project_id: ID of the project whose render to regenerate (either this or render_id must be provided)
            bg_music_volume: Optional override for background music volume (0.0 to 1.0)
            video_audio_volume: Optional override for video audio volume (0.0 to 1.0)
            voiceover_volume: Optional override for voiceover volume (0.0 to 1.0)
            subtitle_enabled: Optional override for subtitle visibility
            color_balance_fix: Optional override for color balance correction
            color_exposure_fix: Optional override for exposure correction
            color_contrast_fix: Optional override for contrast correction
            extend_short_clips: Optional override for extending short clips
            extension_method: Optional override for short clip extension method ('freeze', 'loop', or 'mirror')
            **kwargs: Additional parameters to override in the render
            
        Returns:
            Dictionary with the regeneration job details
        """
        if not render_id and not project_id:
            raise ValueError("Either render_id or project_id must be provided")
            
        data = {}
        
        if render_id:
            data["render_id"] = render_id
        if project_id:
            data["project_id"] = project_id
            
        # Process specific parameters with validation
        # Volume parameters
        if bg_music_volume is not None:
            data["bg_music_volume"] = self._validate_volume(bg_music_volume)
            
        if video_audio_volume is not None:
            data["video_audio_volume"] = self._validate_volume(video_audio_volume)
            
        if voiceover_volume is not None:
            data["voiceover_volume"] = self._validate_volume(voiceover_volume)
        
        # Boolean parameters
        for param_name, param_value in [
            ("subtitle_enabled", subtitle_enabled),
            ("color_balance_fix", color_balance_fix),
            ("color_exposure_fix", color_exposure_fix),
            ("color_contrast_fix", color_contrast_fix),
            ("extend_short_clips", extend_short_clips)
        ]:
            if param_value is not None:
                data[param_name] = bool(param_value)
                
        # Validate extension method
        if extension_method is not None:
            if extension_method not in ["freeze", "loop", "mirror"]:
                raise ValueError("extension_method must be 'freeze', 'loop', or 'mirror'")
            data["extension_method"] = extension_method
        
        # Add any additional override parameters from kwargs
        for key, value in kwargs.items():
            if key not in ["render_id", "project_id"]:
                data[key] = value
            
        return self._make_request("POST", f"{self.render_url}/redo", json_data=data)
    
    def update_render_settings(
        self,
        render_id: Optional[str] = None,
        project_id: Optional[str] = None,
        bg_music_volume: Optional[float] = None,
        video_audio_volume: Optional[float] = None,
        voiceover_volume: Optional[float] = None,
        subtitle_enabled: Optional[bool] = None,
        subtitle_font_size: Optional[int] = None,
        subtitle_color: Optional[Union[str, List[int], Tuple[int, ...]]] = None,
        subtitle_bg_color: Optional[Union[str, List[int], Tuple[int, ...]]] = None,
        subtitle_bg_opacity: Optional[float] = None,
        outro_duration: Optional[float] = None,
        company_name: Optional[str] = None,
        company_subtext: Optional[str] = None,
        call_to_action: Optional[str] = None,
        call_to_action_subtext: Optional[str] = None,
        enable_cta: Optional[bool] = None,
        color_balance_fix: Optional[bool] = None,
        color_exposure_fix: Optional[bool] = None,
        color_contrast_fix: Optional[bool] = None,
        **kwargs
    ) -> Dict:
        """
        Update render settings without regenerating.
        
        Args:
            render_id: ID of the render to update (either this or project_id must be provided)
            project_id: ID of the project whose render to update (either this or render_id must be provided)
            bg_music_volume: New background music volume (0.0 to 1.0)
            video_audio_volume: New video audio volume (0.0 to 1.0)
            voiceover_volume: New voiceover volume (0.0 to 1.0)
            subtitle_enabled: Whether to enable subtitles
            subtitle_font_size: New subtitle text size
            subtitle_color: New subtitle text color (RGB tuple/list or hex string)
            subtitle_bg_color: New subtitle background color (RGB tuple/list or hex string)
            subtitle_bg_opacity: New subtitle background opacity (0.0 to 1.0)
            outro_duration: New duration of the outro in seconds
            company_name: New company name for the outro
            company_subtext: New company tagline for the outro
            call_to_action: New CTA text
            call_to_action_subtext: New CTA subtext
            enable_cta: Whether to show CTA
            color_balance_fix: Whether to apply color balance correction
            color_exposure_fix: Whether to apply exposure correction
            color_contrast_fix: Whether to apply contrast correction
            **kwargs: Additional parameters to update
            
        Returns:
            Dictionary with update confirmation
        """
        if not render_id and not project_id:
            raise ValueError("Either render_id or project_id must be provided")
            
        data = {}
        
        if render_id:
            data["render_id"] = render_id
        if project_id:
            data["project_id"] = project_id
            
        # Process specific parameters with validation
        # Volume parameters
        if bg_music_volume is not None:
            data["bg_music_volume"] = self._validate_volume(bg_music_volume)
            
        if video_audio_volume is not None:
            data["video_audio_volume"] = self._validate_volume(video_audio_volume)
            
        if voiceover_volume is not None:
            data["voiceover_volume"] = self._validate_volume(voiceover_volume)
        
        # Boolean parameters
        for param_name, param_value in [
            ("subtitle_enabled", subtitle_enabled),
            ("enable_cta", enable_cta),
            ("color_balance_fix", color_balance_fix),
            ("color_exposure_fix", color_exposure_fix),
            ("color_contrast_fix", color_contrast_fix)
        ]:
            if param_value is not None:
                data[param_name] = bool(param_value)
        
        # Color parameters
        if subtitle_color is not None:
            data["subtitle_color"] = self._normalize_color(subtitle_color)
            
        if subtitle_bg_color is not None:
            data["subtitle_bg_color"] = self._normalize_color(subtitle_bg_color)
        
        # Other numeric parameters
        if subtitle_font_size is not None:
            data["subtitle_font_size"] = int(subtitle_font_size)
            
        if subtitle_bg_opacity is not None:
            if not 0.0 <= subtitle_bg_opacity <= 1.0:
                warnings.warn(f"subtitle_bg_opacity should be between 0.0 and 1.0, got {subtitle_bg_opacity}")
            data["subtitle_bg_opacity"] = float(subtitle_bg_opacity)
            
        if outro_duration is not None:
            if outro_duration < 0:
                raise ValueError("outro_duration cannot be negative")
            data["outro_duration"] = float(outro_duration)
        
        # String parameters
        for param_name, param_value in [
            ("company_name", company_name),
            ("company_subtext", company_subtext),
            ("call_to_action", call_to_action),
            ("call_to_action_subtext", call_to_action_subtext)
        ]:
            if param_value is not None:
                data[param_name] = str(param_value)
        
        # Add any additional settings from kwargs
        for key, value in kwargs.items():
            if key not in ["render_id", "project_id"]:
                data[key] = value
                
        # Make sure at least one setting is being updated
        if len(data) <= 1:  # Only has ID, no actual updates
            raise ValueError("At least one setting must be provided to update")
            
        return self._make_request("PUT", f"{self.render_url}/update", json_data=data)
    
    def update_render(
        self,
        render_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields_to_update: Optional[List[str]] = None
    ) -> Dict:
        """
        Update a render with the latest sequence data from its source project.
        
        This method pulls the latest data from upstream sources (sequence, brand settings, 
        company details) and updates the render record accordingly.
        
        Args:
            render_id: ID of the render to update (either this or project_id must be provided)
            project_id: ID of the project whose render to update (either this or render_id must be provided)
            fields_to_update: Optional list of specific fields to update from the source data
            
        Returns:
            Dictionary with update confirmation
        """
        if not render_id and not project_id:
            raise ValueError("Either render_id or project_id must be provided")
            
        data = {}
        
        if render_id:
            data["render_id"] = render_id
        if project_id:
            data["project_id"] = project_id
        if fields_to_update:
            if not isinstance(fields_to_update, list):
                raise TypeError("fields_to_update must be a list of strings")
            data["fields_to_update"] = fields_to_update
            
        return self._make_request("PUT", f"{self.render_url}/selfupdate", json_data=data)
    
    def get_render_status(
        self,
        render_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Get the current status of a render job.
        
        This is a convenience method that provides a simplified view of the render status.
        
        Args:
            render_id: ID of the render to check (either this or project_id must be provided)
            project_id: ID of the project whose render to check (either this or render_id must be provided)
            
        Returns:
            Dictionary with render status information including:
            - render_id: The ID of the render
            - project_id: The ID of the associated project
            - status: Current status (PENDING, PROCESSING, COMPLETED, FAILED, or UNKNOWN)
            - created_at: When the render was created
            - updated_at: When the render was last updated
            - is_stale: Whether the render settings have been changed since the last render
        """
        result = self.get_render(render_id, project_id, include_results=True, 
                               include_sequence=False, include_subtitles=False)
        
        # Extract status information for a cleaner response
        status = "UNKNOWN"
        job_result = result.get("job_result", {})
        
        if job_result:
            status = job_result.get("status", "UNKNOWN")
            
        return {
            "render_id": result.get("render_id"),
            "project_id": result.get("project_id"),
            "status": status,
            "created_at": result.get("created_at"),
            "updated_at": result.get("updated_at"),
            "is_stale": result.get("is_stale", False),
            "job_id": result.get("job_id")
        }
    
    def get_render_download_links(
        self,
        render_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Get download and streaming links for a completed render.
        
        This is a convenience method that provides all available download links
        for the rendered video, thumbnail, and subtitles.
        
        Args:
            render_id: ID of the render (either this or project_id must be provided)
            project_id: ID of the project whose render to access (either this or render_id must be provided)
            
        Returns:
            Dictionary with download and streaming URLs:
            - download_url: Direct download link for the rendered video
            - streamable_url: Link for streaming the video
            - thumbnail_streamable_url: Link for the video thumbnail
            - srt_download_url: Link for the SRT subtitle file
            
        Raises:
            Exception: If the render is not yet complete
        """
        result = self.get_render(
            render_id, project_id, 
            include_results=True,
            generate_download_link=True, 
            generate_streamable_link=True, 
            generate_thumbnail_stream_link=True
        )
        
        # Check if render is complete
        job_result = result.get("job_result", {})
        if job_result.get("status") != "COMPLETED":
            raise Exception(f"Render is not yet complete. Current status: {job_result.get('status', 'UNKNOWN')}")
            
        # Extract and return just the links
        links = {
            "render_id": result.get("render_id"),
            "project_id": result.get("project_id"),
            "download_url": result.get("download_url"),
            "download_expires_in": result.get("download_expires_in"),
            "streamable_url": result.get("streamable_url"),
            "streamable_expires_in": result.get("streamable_expires_in"),
            "thumbnail_streamable_url": result.get("thumbnail_streamable_url"),
            "thumbnail_streamable_expires_in": result.get("thumbnail_streamable_expires_in"),
            "srt_download_url": result.get("srt_download_url"),
            "srt_download_expires_in": result.get("srt_download_expires_in")
        }
        
        return links
        
    # Advanced workflows
    
    def create_and_wait_for_render(
        self,
        project_id: str,
        poll_interval: int = 5,
        timeout: int = 3600,
        auto_generate_links: bool = True,
        **kwargs
    ) -> Dict:
        """
        Create a render and wait for it to complete.
        
        This is a convenience workflow that:
        1. Creates a new render
        2. Polls the status until completion or timeout
        3. Returns the final result with download links
        
        Args:
            project_id: ID of the project to render
            poll_interval: How often to check status (in seconds)
            timeout: Maximum time to wait (in seconds)
            auto_generate_links: Whether to automatically generate download links on completion
            **kwargs: Additional parameters for create_render
            
        Returns:
            Dictionary with render details and results
            
        Raises:
            TimeoutError: If the render doesn't complete within the timeout period
            Exception: If the render fails
        """
        # Create the render
        result = self.create_render(project_id=project_id, **kwargs)
        render_id = result.get("render", {}).get("render_id")
        
        if not render_id:
            raise ValueError("Failed to get render_id from response")
        
        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_result = self.get_render_status(render_id=render_id)
            status = status_result.get("status", "UNKNOWN")
            
            if status == "COMPLETED":
                if auto_generate_links:
                    return self.get_render(
                        render_id=render_id,
                        include_results=True,
                        generate_download_link=True,
                        generate_streamable_link=True,
                        generate_thumbnail_stream_link=True
                    )
                else:
                    return self.get_render(render_id=render_id, include_results=True)
            elif status == "FAILED":
                details = self.get_render(render_id=render_id, include_results=True)
                error_message = details.get("job_result", {}).get("error", "Unknown error")
                raise Exception(f"Render failed: {error_message}")
            
            print(f"Render status: {status}. Waiting {poll_interval} seconds...")
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Render did not complete within the timeout of {timeout} seconds")
    
    def update_settings_and_redo(
        self,
        render_id: Optional[str] = None,
        project_id: Optional[str] = None,
        wait_for_completion: bool = False,
        poll_interval: int = 5,
        timeout: int = 3600,
        **kwargs
    ) -> Dict:
        """
        Update render settings and immediately redo the render.
        
        This is a convenience workflow that:
        1. Updates render settings
        2. Redoes the render with updated settings
        3. Optionally waits for completion
        
        Args:
            render_id: ID of the render to update and redo
            project_id: ID of the project whose render to update and redo
            wait_for_completion: Whether to wait for the render to complete
            poll_interval: How often to check status (in seconds) if waiting
            timeout: Maximum time to wait (in seconds) if waiting
            **kwargs: Settings to update
            
        Returns:
            Dictionary with render details and optionally results if waiting
            
        Raises:
            TimeoutError: If waiting and the render doesn't complete within timeout
            Exception: If waiting and the render fails
        """
        # Update settings
        self.update_render_settings(render_id=render_id, project_id=project_id, **kwargs)
        
        # Redo render
        result = self.redo_render(render_id=render_id, project_id=project_id)
        new_job_id = result.get("job_id")
        render_id = result.get("render_id")
        
        if wait_for_completion:
            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                status_result = self.get_render_status(render_id=render_id)
                status = status_result.get("status", "UNKNOWN")
                
                if status == "COMPLETED":
                    return self.get_render(
                        render_id=render_id,
                        include_results=True,
                        generate_download_link=True,
                        generate_streamable_link=True,
                        generate_thumbnail_stream_link=True
                    )
                elif status == "FAILED":
                    details = self.get_render(render_id=render_id, include_results=True)
                    error_message = details.get("job_result", {}).get("error", "Unknown error")
                    raise Exception(f"Render failed: {error_message}")
                
                print(f"Render status: {status}. Waiting {poll_interval} seconds...")
                time.sleep(poll_interval)
                
            raise TimeoutError(f"Render did not complete within the timeout of {timeout} seconds")
        
        return result
