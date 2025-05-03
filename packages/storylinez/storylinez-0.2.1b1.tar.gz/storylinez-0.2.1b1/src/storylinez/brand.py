import os
import json
import requests
from typing import Dict, List, Optional, Union, Any, Tuple, cast
import re
import warnings
from .base_client import BaseClient

class BrandClient(BaseClient):
    """
    Client for interacting with Storylinez Brand API.
    Provides methods for managing brand presets and styling.
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.storylinezads.com", default_org_id: str = None):
        """
        Initialize the BrandClient.
        
        Args:
            api_key: Your Storylinez API Key
            api_secret: Your Storylinez API Secret
            base_url: Base URL for the API (defaults to production)
            default_org_id: Default organization ID to use for all API calls (optional)
        """
        super().__init__(api_key, api_secret, base_url, default_org_id)
        self.brand_url = f"{self.base_url}/brand"
        
        # Define allowed logo image formats (matching the image standards in the SDK)
        self.allowed_logo_formats = ['jpg', 'jpeg', 'png']
    
    @staticmethod
    def validate_rgb(color) -> List[int]:
        """
        Validates and converts a color value to RGB format.
        
        Args:
            color: Can be a list/tuple of RGB values, a hex string, or a CSS color name
            
        Returns:
            List of RGB values [r, g, b]
        
        Raises:
            ValueError: If the color format is invalid or unsupported
        """
        # Already RGB list/tuple
        if isinstance(color, (list, tuple)) and len(color) == 3:
            return [int(c) for c in color]
        
        # Hex color code (with or without #)
        elif isinstance(color, str):
            # Strip # if present
            hex_color = color.lstrip('#')
            
            # Standard hex format #RRGGBB
            if re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return [r, g, b]
            
            # Shorthand hex format #RGB
            elif re.match(r'^[0-9A-Fa-f]{3}$', hex_color):
                r = int(hex_color[0] + hex_color[0], 16)
                g = int(hex_color[1] + hex_color[1], 16)
                b = int(hex_color[2] + hex_color[2], 16)
                return [r, g, b]
            
            # CSS color names could be implemented here if needed
            # For now, just raise an error for unrecognized formats
            else:
                raise ValueError(f"Color '{color}' is not a valid hex color. Use format '#RRGGBB' or [R,G,B] list.")
        else:
            raise ValueError(f"Color must be an RGB list/tuple or a hex string. Got {type(color)} instead.")

    @staticmethod
    def validate_logo_key(logo_key: Optional[str]) -> Optional[str]:
        """
        Validates that a logo key follows the proper format.
        
        Args:
            logo_key: The S3 key for the logo
            
        Returns:
            The validated logo key
            
        Raises:
            ValueError: If logo_key is invalid
        """
        if logo_key is None:
            return None
        
        if not isinstance(logo_key, str):
            raise ValueError(f"Logo key must be a string. Got {type(logo_key)} instead.")
        
        if not logo_key.startswith("userdata/"):
            raise ValueError("Logo key must start with 'userdata/'.")
        
        return logo_key

    def get_logo_upload_url(self, filename: str, org_id: Optional[str] = None) -> Dict:
        """
        Generate a secure upload link for a brand logo.
        
        Args:
            filename: Name of the logo file to upload (must be jpg, jpeg, or png)
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with upload details (upload_link, key, upload_id, expires_in)
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if not filename:
            raise ValueError("Filename is required.")
            
        # Check file extension - only allow jpg, jpeg, png
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if ext not in self.allowed_logo_formats:
            raise ValueError(f"File extension '{ext}' not allowed for logos. Use one of: {', '.join(self.allowed_logo_formats)}")
            
        params = {
            "org_id": org_id,
            "filename": filename
        }
        
        return self._make_request("GET", "logo-upload-url", params=params)
    
    def upload_logo(
        self, 
        file_path: str, 
        org_id: Optional[str] = None, 
        name: Optional[str] = None,
        is_default: bool = False,
        is_public: bool = False,
        create_brand: bool = True,
        **kwargs
    ) -> Dict:
        """
        Upload a logo file for brands.
        This is a convenience method that handles the full process: generating upload link, uploading, and optionally creating brand.
        
        Args:
            file_path: Path to the logo file on local disk (must be jpg, jpeg, or png)
            org_id: Organization ID (uses default if not provided)
            name: Brand name (defaults to filename without extension if not provided)
            is_default: Whether this brand should be the default 
            is_public: Whether this brand should be publicly accessible
            create_brand: Whether to create a brand with this logo (defaults to True)
            **kwargs: Additional brand styling parameters if creating a brand
        
        Returns:
            Dictionary with upload details or created brand details if create_brand is True
            
        Raises:
            ValueError: If file_path is invalid or has unsupported extension
            FileNotFoundError: If the file doesn't exist
            Exception: If upload fails
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Validate file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found at '{file_path}'")
            
        # Get file information and validate extension
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if ext not in self.allowed_logo_formats:
            raise ValueError(f"File extension '{ext}' not allowed for logos. Use one of: {', '.join(self.allowed_logo_formats)}")
        
        # Generate upload link
        upload_info = self.get_logo_upload_url(filename=filename, org_id=org_id)
        
        # Upload the file to the pre-signed URL
        upload_link = upload_info.get("upload_link")
        logo_key = upload_info.get("s3_key")
        upload_id = upload_info.get("upload_id")
        
        if not upload_link:
            raise ValueError("Failed to generate upload URL")
        
        # Use requests to upload the file
        try:
            with open(file_path, 'rb') as file_data:
                upload_response = requests.put(upload_link, data=file_data)
                
                if upload_response.status_code >= 400:
                    raise Exception(f"Logo upload failed with status {upload_response.status_code}: {upload_response.text}")
        except Exception as e:
            raise Exception(f"Error uploading logo: {str(e)}")
        
        # Return early if not creating brand
        if not create_brand:
            return {
                "upload_id": upload_id,
                "s3_key": logo_key,
                "message": "Logo uploaded successfully"
            }
        
        # Use filename without extension as default name if not provided
        if not name:
            name = os.path.splitext(filename)[0]
            
        # Create brand with the uploaded logo
        return self.create(
            name=name,
            logo_key=logo_key,
            is_default=is_default,
            is_public=is_public,
            org_id=org_id,
            **kwargs
        )
        
    def create(
        self, 
        name: str,
        org_id: Optional[str] = None,
        logo_key: Optional[str] = None,
        is_default: bool = False,
        is_public: bool = False,
        # Outro settings
        outro_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        outro_logo_size: Optional[Union[List[int], Tuple[int, ...]]] = None,
        outro_logo_mode: Optional[int] = None,
        outro_transition: Optional[str] = None,
        outro_transition_duration: Optional[float] = None,
        # Font settings
        company_font: Optional[str] = None,
        company_font_size: Optional[int] = None,
        subtext_font: Optional[str] = None,
        subtext_font_size: Optional[int] = None,
        text_spacing: Optional[int] = None,
        logo_text_spacing: Optional[int] = None,
        # Text colors
        main_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        sub_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        # Transition settings
        transition_duration: Optional[float] = None,
        text_transition: Optional[str] = None,
        text_transition_delay: Optional[float] = None,
        text_transition_duration: Optional[float] = None,
        # CTA settings
        cta_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        cta_subtext_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        cta_company_font_size: Optional[int] = None,
        cta_subtext_font_size: Optional[int] = None,
        cta_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        # Subtitle settings
        subtitle_font_size: Optional[int] = None,
        subtitle_font: Optional[str] = None,
        subtitle_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        subtitle_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        subtitle_bg_opacity: Optional[float] = None,
        subtitle_bg_padding: Optional[int] = None,
        subtitle_bg_rounded: Optional[bool] = None,
        subtitle_bg_corner_radius: Optional[int] = None,
        subtitle_position: Optional[int] = None,
        subtitle_squeeze_xp: Optional[int] = None,
        subtitle_max_group_size: Optional[int] = None,
        # Template settings
        template_heading_font_size: Optional[int] = None,
        template_heading_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_description_font_size: Optional[int] = None,
        template_description_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_bg_opacity: Optional[float] = None,
        template_heading_font: Optional[str] = None,
        template_description_font: Optional[str] = None,
        template_text_spacing: Optional[int] = None,
        template_xp: Optional[int] = None,
        template_yp: Optional[int] = None,
        template_text_align: Optional[str] = None,
        template_text_transition: Optional[str] = None,
        template_text_transition_delay: Optional[float] = None,
        template_text_transition_duration: Optional[float] = None,
        template_bg_rounded: Optional[bool] = None,
        template_bg_corner_radius: Optional[int] = None,
        # Other settings
        image_slideshow: Optional[bool] = None,
        **kwargs  # For backward compatibility
    ) -> Dict:
        """
        Create a new brand preset with styling configurations.
        
        Args:
            name: Brand name
            org_id: Organization ID (uses default if not provided)
            logo_key: S3 key of the uploaded logo (optional)
            is_default: Whether this brand should be the default
            is_public: Whether this brand should be publicly accessible
            
            # Outro settings
            outro_bg_color: RGB color for outro background (list, tuple, or hex string)
            outro_logo_size: Logo dimensions as [width, height]
            outro_logo_mode: Mode for displaying logo (0: text only, 1: logo only, 2: both)
            outro_transition: Transition effect for outro appearance (e.g., "fade")
            outro_transition_duration: Duration of outro transition in seconds
            
            # Font settings
            company_font: Font for company name
            company_font_size: Font size for company name
            subtext_font: Font for secondary text
            subtext_font_size: Font size for subtext
            text_spacing: Vertical spacing between text elements
            logo_text_spacing: Spacing between logo and text
            
            # Text colors
            main_text_color: RGB color for main text (list, tuple, or hex string)
            sub_text_color: RGB color for secondary text (list, tuple, or hex string)
            
            # Transition settings
            transition_duration: Default duration for transitions in seconds
            text_transition: Transition effect for text elements
            text_transition_delay: Delay before text transition begins
            text_transition_duration: Duration of text transitions
            
            # CTA settings
            cta_text_color: RGB color for CTA text
            cta_subtext_color: RGB color for CTA subtext
            cta_company_font_size: Font size for company name in CTA
            cta_subtext_font_size: Font size for subtext in CTA
            cta_bg_color: RGB background color for CTA
            
            # Subtitle settings
            subtitle_font_size: Font size for subtitles
            subtitle_font: Font for subtitles
            subtitle_color: RGB color for subtitle text
            subtitle_bg_color: RGB background color for subtitles
            subtitle_bg_opacity: Opacity for subtitle background (0.0-1.0)
            subtitle_bg_padding: Padding around subtitle text
            subtitle_bg_rounded: Whether subtitle background has rounded corners
            subtitle_bg_corner_radius: Corner radius for subtitle background
            subtitle_position: Position of subtitles (0-4)
            subtitle_squeeze_xp: Width threshold for subtitle squeezing
            subtitle_max_group_size: Max number of subtitle lines to group together
            
            # Template settings
            template_heading_font_size: Font size for template headings
            template_heading_color: RGB color for template headings
            template_description_font_size: Font size for template descriptions
            template_description_color: RGB color for template descriptions
            template_bg_color: RGB background color for templates
            template_bg_opacity: Opacity for template background (0.0-1.0)
            template_heading_font: Font for template headings
            template_description_font: Font for template descriptions
            template_text_spacing: Spacing between template text elements
            template_xp: X-coordinate for template text positioning
            template_yp: Y-coordinate for template text positioning
            template_text_align: Alignment of template text (left, center, right)
            template_text_transition: Transition effect for template text
            template_text_transition_delay: Delay before template text transition
            template_text_transition_duration: Duration of template text transition
            template_bg_rounded: Whether template background has rounded corners
            template_bg_corner_radius: Corner radius for template background
            
            # Other settings
            image_slideshow: Whether to enable image slideshow effects
            
            **kwargs: Additional brand styling parameters for backward compatibility
        
        Returns:
            Dictionary with created brand details
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not name:
            raise ValueError("Brand name is required.")
            
        # Validate logo key if provided
        logo_key = self.validate_logo_key(logo_key)
            
        # Start building data payload
        data = {
            "org_id": org_id,
            "name": name,
            "is_default": is_default,
            "is_public": is_public
        }
        
        if logo_key:
            data["logo_key"] = logo_key
            
        # Process color parameters and convert to RGB if needed
        color_params = {
            "outro_bg_color": outro_bg_color,
            "main_text_color": main_text_color,
            "sub_text_color": sub_text_color,
            "cta_text_color": cta_text_color,
            "cta_subtext_color": cta_subtext_color,
            "cta_bg_color": cta_bg_color,
            "subtitle_color": subtitle_color,
            "subtitle_bg_color": subtitle_bg_color,
            "template_heading_color": template_heading_color,
            "template_description_color": template_description_color,
            "template_bg_color": template_bg_color
        }
        
        for param_name, color_value in color_params.items():
            if color_value is not None:
                try:
                    data[param_name] = self.validate_rgb(color_value)
                except ValueError as e:
                    raise ValueError(f"Invalid {param_name}: {str(e)}")
        
        # Process size parameters
        if outro_logo_size is not None:
            if not isinstance(outro_logo_size, (list, tuple)) or len(outro_logo_size) != 2:
                raise ValueError("outro_logo_size must be a list or tuple with two integers [width, height]")
            data["outro_logo_size"] = list(outro_logo_size)
        
        # Add all other provided parameters
        for key, value in [
            # Outro settings
            ("outro_logo_mode", outro_logo_mode),
            ("outro_transition", outro_transition),
            ("outro_transition_duration", outro_transition_duration),
            
            # Font settings
            ("company_font", company_font),
            ("company_font_size", company_font_size),
            ("subtext_font", subtext_font),
            ("subtext_font_size", subtext_font_size),
            ("text_spacing", text_spacing),
            ("logo_text_spacing", logo_text_spacing),
            
            # Transition settings
            ("transition_duration", transition_duration),
            ("text_transition", text_transition),
            ("text_transition_delay", text_transition_delay),
            ("text_transition_duration", text_transition_duration),
            
            # CTA settings
            ("cta_company_font_size", cta_company_font_size),
            ("cta_subtext_font_size", cta_subtext_font_size),
            
            # Subtitle settings
            ("subtitle_font_size", subtitle_font_size),
            ("subtitle_font", subtitle_font),
            ("subtitle_bg_opacity", subtitle_bg_opacity),
            ("subtitle_bg_padding", subtitle_bg_padding),
            ("subtitle_bg_rounded", subtitle_bg_rounded),
            ("subtitle_bg_corner_radius", subtitle_bg_corner_radius),
            ("subtitle_position", subtitle_position),
            ("subtitle_squeeze_xp", subtitle_squeeze_xp),
            ("subtitle_max_group_size", subtitle_max_group_size),
            
            # Template settings
            ("template_heading_font_size", template_heading_font_size),
            ("template_description_font_size", template_description_font_size),
            ("template_bg_opacity", template_bg_opacity),
            ("template_heading_font", template_heading_font),
            ("template_description_font", template_description_font),
            ("template_text_spacing", template_text_spacing),
            ("template_xp", template_xp),
            ("template_yp", template_yp),
            ("template_text_align", template_text_align),
            ("template_text_transition", template_text_transition),
            ("template_text_transition_delay", template_text_transition_delay),
            ("template_text_transition_duration", template_text_transition_duration),
            ("template_bg_rounded", template_bg_rounded),
            ("template_bg_corner_radius", template_bg_corner_radius),
            
            # Other settings
            ("image_slideshow", image_slideshow)
        ]:
            if value is not None:
                data[key] = value
        
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
        
        return self._make_request("POST", "create", json_data=data)
    
    def get_all(
        self, 
        org_id: Optional[str] = None,
        page: int = 1, 
        limit: int = 10, 
        include_urls: bool = True
    ) -> Dict:
        """
        Get all brand presets for an organization with pagination.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            page: Page number to retrieve
            limit: Number of items per page
            include_urls: Whether to include pre-signed URLs for logos
        
        Returns:
            Dictionary with brand list and pagination info
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
        
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")
            
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
            
        params = {
            "org_id": org_id,
            "page": page,
            "limit": limit,
            "include_urls": str(include_urls).lower()
        }
        
        return self._make_request("GET", "get_all", params=params)
    
    def get(self, brand_id: Optional[str] = None, org_id: Optional[str] = None) -> Dict:
        """
        Get a specific brand preset or the default for an organization.
        
        Args:
            brand_id: ID of the brand (if None, gets default)
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with the brand details including styling
            
        Raises:
            ValueError: If neither brand_id nor org_id is provided
        """
        org_id = org_id or self.default_org_id
        if not org_id and not brand_id:
            raise ValueError("Either brand_id or org_id is required.")
            
        params = {}
        if brand_id:
            params["brand_id"] = brand_id
        if org_id:
            params["org_id"] = org_id
        
        return self._make_request("GET", "get", params=params)
    
    def get_default(self, org_id: Optional[str] = None) -> Dict:
        """
        Get the default brand preset for an organization using the dedicated endpoint.
        
        Args:
            org_id: Organization ID (uses default if not provided)
        
        Returns:
            Dictionary with the default brand details including styling
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        params = {"org_id": org_id}
        return self._make_request("GET", "get_default", params=params)
    
    def update(
        self, 
        brand_id: str,
        # Updated fields
        name: Optional[str] = None,
        is_default: Optional[bool] = None,
        is_public: Optional[bool] = None,
        logo_key: Optional[str] = None,
        logo_upload_id: Optional[str] = None,  # Added more specific logo upload parameter
        upload_id: Optional[str] = None,       # Keep original for backward compatibility
        # Outro settings
        outro_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        outro_logo_size: Optional[Union[List[int], Tuple[int, ...]]] = None,
        outro_logo_mode: Optional[int] = None,
        outro_transition: Optional[str] = None,
        outro_transition_duration: Optional[float] = None,
        # Font settings
        company_font: Optional[str] = None,
        company_font_size: Optional[int] = None,
        subtext_font: Optional[str] = None,
        subtext_font_size: Optional[int] = None,
        text_spacing: Optional[int] = None,
        logo_text_spacing: Optional[int] = None,
        # Text colors
        main_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        sub_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        # Transition settings
        transition_duration: Optional[float] = None,
        text_transition: Optional[str] = None,
        text_transition_delay: Optional[float] = None,
        text_transition_duration: Optional[float] = None,
        # CTA settings
        cta_text_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        cta_subtext_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        cta_company_font_size: Optional[int] = None,
        cta_subtext_font_size: Optional[int] = None,
        cta_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        # Subtitle settings
        subtitle_font_size: Optional[int] = None,
        subtitle_font: Optional[str] = None,
        subtitle_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        subtitle_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        subtitle_bg_opacity: Optional[float] = None,
        subtitle_bg_padding: Optional[int] = None,
        subtitle_bg_rounded: Optional[bool] = None,
        subtitle_bg_corner_radius: Optional[int] = None,
        subtitle_position: Optional[int] = None,
        subtitle_squeeze_xp: Optional[int] = None,
        subtitle_max_group_size: Optional[int] = None,
        # Template settings
        template_heading_font_size: Optional[int] = None,
        template_heading_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_description_font_size: Optional[int] = None,
        template_description_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_bg_color: Optional[Union[List[int], Tuple[int, ...], str]] = None,
        template_bg_opacity: Optional[float] = None,
        template_heading_font: Optional[str] = None,
        template_description_font: Optional[str] = None,
        template_text_spacing: Optional[int] = None,
        template_xp: Optional[int] = None,
        template_yp: Optional[int] = None,
        template_text_align: Optional[str] = None,
        template_text_transition: Optional[str] = None,
        template_text_transition_delay: Optional[float] = None,
        template_text_transition_duration: Optional[float] = None,
        template_bg_rounded: Optional[bool] = None,
        template_bg_corner_radius: Optional[int] = None,
        # Other settings
        image_slideshow: Optional[bool] = None,
        **kwargs  # For backward compatibility
    ) -> Dict:
        """
        Update a brand preset's properties.
        
        Args:
            brand_id: ID of the brand to update
            name: New brand name
            is_default: Whether this brand should be default
            is_public: Whether this brand is public
            logo_key: New S3 key for the logo
            logo_upload_id: Upload ID specifically for logo uploads (preferred over generic upload_id)
            upload_id: Legacy parameter for backward compatibility
            
            # Plus all the same styling parameters as in the create method
            # All parameters are optional - only specified ones will be updated
            
            **kwargs: Additional brand styling parameters for backward compatibility
            
        Returns:
            Dictionary with the updated brand details
            
        Raises:
            ValueError: If brand_id is not provided or parameters are invalid
        """
        if not brand_id:
            raise ValueError("brand_id is required.")
            
        # Validate logo key if provided
        logo_key = self.validate_logo_key(logo_key)
            
        # Start building data payload
        data = {}
        
        # Add name to update if provided and not empty
        if name is not None:
            if not name.strip():
                raise ValueError("Brand name cannot be empty.")
            data["name"] = name
            
        # Add basic boolean fields
        if is_default is not None:
            data["is_default"] = is_default
            
        if is_public is not None:
            data["is_public"] = is_public
            
        if logo_key is not None:
            data["logo_key"] = logo_key
        
        # Add the explicit logo upload ID if provided (new parameter, more specific)
        if logo_upload_id is not None:
            data["logo_upload_id"] = logo_upload_id
        # Otherwise, fall back to the generic upload_id parameter if provided (for backward compatibility)
        elif upload_id is not None:
            data["upload_id"] = upload_id
        
        # Process color parameters and convert to RGB if needed
        color_params = {
            "outro_bg_color": outro_bg_color,
            "main_text_color": main_text_color,
            "sub_text_color": sub_text_color,
            "cta_text_color": cta_text_color,
            "cta_subtext_color": cta_subtext_color,
            "cta_bg_color": cta_bg_color,
            "subtitle_color": subtitle_color,
            "subtitle_bg_color": subtitle_bg_color,
            "template_heading_color": template_heading_color,
            "template_description_color": template_description_color,
            "template_bg_color": template_bg_color
        }
        
        for param_name, color_value in color_params.items():
            if color_value is not None:
                try:
                    data[param_name] = self.validate_rgb(color_value)
                except ValueError as e:
                    raise ValueError(f"Invalid {param_name}: {str(e)}")
        
        # Process size parameters
        if outro_logo_size is not None:
            if not isinstance(outro_logo_size, (list, tuple)) or len(outro_logo_size) != 2:
                raise ValueError("outro_logo_size must be a list or tuple with two integers [width, height]")
            data["outro_logo_size"] = list(outro_logo_size)
        
        # Add all other provided parameters
        for key, value in [
            # Outro settings
            ("outro_logo_mode", outro_logo_mode),
            ("outro_transition", outro_transition),
            ("outro_transition_duration", outro_transition_duration),
            
            # Font settings
            ("company_font", company_font),
            ("company_font_size", company_font_size),
            ("subtext_font", subtext_font),
            ("subtext_font_size", subtext_font_size),
            ("text_spacing", text_spacing),
            ("logo_text_spacing", logo_text_spacing),
            
            # Transition settings
            ("transition_duration", transition_duration),
            ("text_transition", text_transition),
            ("text_transition_delay", text_transition_delay),
            ("text_transition_duration", text_transition_duration),
            
            # CTA settings
            ("cta_company_font_size", cta_company_font_size),
            ("cta_subtext_font_size", cta_subtext_font_size),
            
            # Subtitle settings
            ("subtitle_font_size", subtitle_font_size),
            ("subtitle_font", subtitle_font),
            ("subtitle_bg_opacity", subtitle_bg_opacity),
            ("subtitle_bg_padding", subtitle_bg_padding),
            ("subtitle_bg_rounded", subtitle_bg_rounded),
            ("subtitle_bg_corner_radius", subtitle_bg_corner_radius),
            ("subtitle_position", subtitle_position),
            ("subtitle_squeeze_xp", subtitle_squeeze_xp),
            ("subtitle_max_group_size", subtitle_max_group_size),
            
            # Template settings
            ("template_heading_font_size", template_heading_font_size),
            ("template_description_font_size", template_description_font_size),
            ("template_bg_opacity", template_bg_opacity),
            ("template_heading_font", template_heading_font),
            ("template_description_font", template_description_font),
            ("template_text_spacing", template_text_spacing),
            ("template_xp", template_xp),
            ("template_yp", template_yp),
            ("template_text_align", template_text_align),
            ("template_text_transition", template_text_transition),
            ("template_text_transition_delay", template_text_transition_delay),
            ("template_text_transition_duration", template_text_transition_duration),
            ("template_bg_rounded", template_bg_rounded),
            ("template_bg_corner_radius", template_bg_corner_radius),
            
            # Other settings
            ("image_slideshow", image_slideshow)
        ]:
            if value is not None:
                data[key] = value
        
        # Add any additional kwargs for backward compatibility
        data.update(kwargs)
        
        # Ensure we have something to update
        if not data:
            raise ValueError("No update parameters provided.")
            
        params = {"brand_id": brand_id}
        return self._make_request("PUT", "update", params=params, json_data=data)
    
    def delete(self, brand_id: str) -> Dict:
        """
        Delete a brand preset.
        
        Args:
            brand_id: ID of the brand to delete
            
        Returns:
            Dictionary with deletion confirmation
            
        Raises:
            ValueError: If brand_id is not provided
        """
        if not brand_id:
            raise ValueError("brand_id is required.")
            
        params = {"brand_id": brand_id}
        return self._make_request("DELETE", "delete", params=params)
    
    def set_default(self, brand_id: str) -> Dict:
        """
        Set a brand preset as the default.
        
        Args:
            brand_id: ID of the brand to set as default
            
        Returns:
            Dictionary with confirmation message
            
        Raises:
            ValueError: If brand_id is not provided
        """
        if not brand_id:
            raise ValueError("brand_id is required.")
            
        params = {"brand_id": brand_id}
        return self._make_request("PUT", "set_default", params=params)
    
    def add_logo(self, brand_id: str, upload_id: Optional[str] = None, logo_key: Optional[str] = None) -> Dict:
        """
        Add or update a logo for a brand.
        
        Args:
            brand_id: ID of the brand to update
            upload_id: Upload ID from a logo upload process
            logo_key: S3 key of the uploaded logo
            
        Returns:
            Dictionary with the updated brand details including logo URL
            
        Raises:
            ValueError: If brand_id is not provided or both upload_id and logo_key are missing
        """
        if not brand_id:
            raise ValueError("brand_id is required.")
        if not logo_key and not upload_id:
            raise ValueError("Either logo_key or upload_id is required.")
            
        data = {}
        if logo_key:
            logo_key = self.validate_logo_key(logo_key)
            data["logo_key"] = logo_key
        if upload_id:
            data["upload_id"] = upload_id
        
        params = {"brand_id": brand_id}
        return self._make_request("PUT", "add_logo", params=params, json_data=data)
    
    def duplicate(
        self, 
        brand_id: str, 
        org_id: Optional[str] = None, 
        name: Optional[str] = None
    ) -> Dict:
        """
        Duplicate a brand preset.
        
        Args:
            brand_id: ID of the brand to duplicate
            org_id: Target organization ID (uses default if not provided)
            name: Name for the duplicated brand (optional)
            
        Returns:
            Dictionary with the duplicated brand
            
        Raises:
            ValueError: If brand_id is not provided or org_id is missing
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        if not brand_id:
            raise ValueError("brand_id is required.")
            
        data = {
            "brand_id": brand_id,
            "org_id": org_id
        }
        
        if name:
            data["name"] = name
        
        return self._make_request("POST", "duplicate", json_data=data)
    
    def get_fonts(self) -> Dict:
        """
        Get a list of available fonts for brand styling.
        
        Returns:
            Dictionary with available fonts
        """
        return self._make_request("GET", "fonts")
    
    def get_public_brands(
        self, 
        exclude_org_id: Optional[str] = None, 
        page: int = 1, 
        limit: int = 20, 
        include_logos: bool = False
    ) -> Dict:
        """
        Get publicly available brand presets.
        
        Args:
            exclude_org_id: Organization ID to exclude from results
            page: Page number to retrieve
            limit: Number of items per page
            include_logos: Whether to include logo URLs
            
        Returns:
            Dictionary with public brands and pagination info
            
        Raises:
            ValueError: If pagination parameters are invalid
        """
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")
            
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        params = {
            "page": page,
            "limit": limit,
            "include_logos": str(include_logos).lower()
        }
        
        if exclude_org_id:
            params["exclude_org_id"] = exclude_org_id
        
        return self._make_request("GET", "public", params=params)
    
    def search(
        self, 
        query: str = "", 
        include_public: bool = True, 
        org_id: Optional[str] = None,
        page: int = 1, 
        limit: int = 20,
        include_logos: bool = False
    ) -> Dict:
        """
        Search for brand presets.
        
        Args:
            query: Search term for brand names
            include_public: Whether to include public brands
            org_id: Organization ID to limit search to (optional)
            page: Page number to retrieve
            limit: Number of items per page
            include_logos: Whether to include logo URLs
            
        Returns:
            Dictionary with search results and pagination info
            
        Raises:
            ValueError: If pagination parameters are invalid
        """
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")
            
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        params = {
            "q": query,
            "include_public": str(include_public).lower(),
            "page": page,
            "limit": limit,
            "include_logos": str(include_logos).lower()
        }
        
        if org_id:
            params["org_id"] = org_id
        
        return self._make_request("GET", "search", params=params)
    
    # Workflow Methods
    
    def create_or_update_brand_with_logo(
        self, 
        name: str, 
        logo_path: str, 
        brand_id: Optional[str] = None,
        org_id: Optional[str] = None,
        **brand_params
    ) -> Dict:
        """
        Workflow method that creates a new brand with a logo or updates an existing brand.
        
        Args:
            name: Brand name
            logo_path: Path to logo file (must be jpg, jpeg, or png)
            brand_id: Existing brand ID if updating
            org_id: Organization ID (uses default if not provided)
            **brand_params: Additional brand styling parameters
            
        Returns:
            Dictionary with created or updated brand details
            
        Raises:
            ValueError: If required parameters are missing or logo format is invalid
            FileNotFoundError: If the logo file doesn't exist
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        # Validate logo file exists
        if not os.path.isfile(logo_path):
            raise FileNotFoundError(f"Logo file not found at '{logo_path}'")
            
        # Get file name and validate extension
        filename = os.path.basename(logo_path)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if ext not in self.allowed_logo_formats:
            raise ValueError(f"File extension '{ext}' not allowed for logos. Use one of: {', '.join(self.allowed_logo_formats)}")
        
        # 1. Upload logo first
        upload_info = self.get_logo_upload_url(filename=filename, org_id=org_id)
        upload_link = upload_info.get("upload_link")
        logo_key = upload_info.get("s3_key")
        upload_id = upload_info.get("upload_id")
        
        # 2. Upload the actual file
        try:
            with open(logo_path, 'rb') as file_data:
                upload_response = requests.put(upload_link, data=file_data)
                
                if upload_response.status_code >= 400:
                    raise Exception(f"Logo upload failed with status {upload_response.status_code}")
        except Exception as e:
            raise Exception(f"Error uploading logo: {str(e)}")
        
        # 3. Now either update existing brand or create a new one
        if brand_id:
            # Update existing brand with logo
            result = self.add_logo(brand_id=brand_id, upload_id=upload_id)
            
            # If there are other brand params to update, do that too
            if brand_params:
                result = self.update(brand_id=brand_id, **brand_params)
                
            return result
        else:
            # Create new brand with uploaded logo and other params
            return self.create(
                name=name,
                org_id=org_id,
                logo_key=logo_key,
                **brand_params
            )

    def find_or_create_default_brand(
        self, 
        org_id: Optional[str] = None,
        brand_name: str = "Default Brand",
        create_if_missing: bool = True,
        **brand_params
    ) -> Dict:
        """
        Gets the default brand for an organization or creates one if it doesn't exist.
        
        Args:
            org_id: Organization ID (uses default if not provided)
            brand_name: Name to use for new brand if creating
            create_if_missing: Whether to create a default brand if none exists
            **brand_params: Brand parameters to use if creating
            
        Returns:
            Dictionary with brand details
            
        Raises:
            ValueError: If org_id is not provided
        """
        org_id = org_id or self.default_org_id
        if not org_id:
            raise ValueError("Organization ID is required. Either provide org_id parameter or set a default_org_id when initializing the client.")
            
        try:
            # Try to get default brand
            return self.get_default(org_id=org_id)
        except Exception as e:
            # If no default brand exists and we're allowed to create
            if create_if_missing:
                warnings.warn(f"No default brand found, creating one named '{brand_name}'")
                return self.create(
                    name=brand_name,
                    org_id=org_id,
                    is_default=True,
                    **brand_params
                )
            else:
                raise Exception(f"No default brand found for organization {org_id} and create_if_missing=False") from e

    def update_brand_with_logo(
        self,
        brand_id: str,
        logo_path: str,
        **brand_params
    ) -> Dict:
        """
        Updates an existing brand with a new logo using the logo_upload_id parameter.
        This workflow method handles the full process of generating an upload URL,
        uploading the logo file, and updating the brand with the new logo.
        
        Args:
            brand_id: ID of the brand to update
            logo_path: Path to logo file (must be jpg, jpeg, or png)
            **brand_params: Additional brand parameters to update
            
        Returns:
            Dictionary with the updated brand details
            
        Raises:
            ValueError: If required parameters are missing or logo format is invalid
            FileNotFoundError: If the logo file doesn't exist
        """
        # Validate brand_id
        if not brand_id:
            raise ValueError("brand_id is required.")
            
        # Get brand details to determine org_id
        brand = self.get(brand_id=brand_id)
        org_id = brand.get('org_id')
        
        # Validate logo file exists
        if not os.path.isfile(logo_path):
            raise FileNotFoundError(f"Logo file not found at '{logo_path}'")
            
        # Get file name and validate extension
        filename = os.path.basename(logo_path)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if ext not in self.allowed_logo_formats:
            raise ValueError(f"File extension '{ext}' not allowed for logos. Use one of: {', '.join(self.allowed_logo_formats)}")
        
        # 1. Get upload URL
        upload_info = self.get_logo_upload_url(filename=filename, org_id=org_id)
        upload_link = upload_info.get("upload_link")
        upload_id = upload_info.get("upload_id")
        
        # 2. Upload the actual file
        try:
            with open(logo_path, 'rb') as file_data:
                upload_response = requests.put(upload_link, data=file_data)
                
                if upload_response.status_code >= 400:
                    raise Exception(f"Logo upload failed with status {upload_response.status_code}: {upload_response.text}")
        except Exception as e:
            raise Exception(f"Error uploading logo: {str(e)}")
        
        # 3. Update the brand using logo_upload_id
        update_params = {"logo_upload_id": upload_id}
        update_params.update(brand_params)
        return self.update(brand_id=brand_id, **update_params)
