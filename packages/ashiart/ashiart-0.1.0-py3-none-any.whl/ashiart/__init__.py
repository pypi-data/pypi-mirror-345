"""ASCII Art Generator Package."""

from .generator import AsciiArtGenerator, image_to_ascii

try:
    from .enhanced import (
        EnhancedAsciiArtGenerator, 
        image_to_enhanced_ascii, 
        image_to_html_ascii
    )
    HAS_ENHANCED = True
except ImportError:
    # Some dependencies might be missing (numpy)
    HAS_ENHANCED = False

__version__ = "0.1.0"
__all__ = ["AsciiArtGenerator", "image_to_ascii"]

if HAS_ENHANCED:
    __all__ += ["EnhancedAsciiArtGenerator", "image_to_enhanced_ascii", "image_to_html_ascii"] 