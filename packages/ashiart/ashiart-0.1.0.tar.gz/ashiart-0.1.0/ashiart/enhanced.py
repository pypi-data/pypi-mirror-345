"""Enhanced ASCII Art Generator with advanced features."""

import os
import math
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter


class EnhancedAsciiArtGenerator:
    """An enhanced ASCII art generator with advanced features."""

    # Default ASCII characters from darkest to lightest
    ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    
    # High-density character set (70 shades)
    DENSE_CHARS = ["$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", 
                   "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", 
                   "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", 
                   "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", 
                   ">", "i", "!", "l", "I", ";", ":", "\"", "^", "`", "'", ".", " "]
    
    # Unicode block characters for higher resolution
    BLOCK_CHARS = ["█", "▓", "▒", "░", " "]
    
    # Unicode braille patterns (can represent 8 pixels per character)
    BRAILLE_CHARS = [chr(0x2800 + i) for i in range(256)]

    def __init__(self, chars=None, width=100, height=None, mode="standard"):
        """
        Initialize the enhanced ASCII art generator.
        
        Args:
            chars (list, optional): ASCII characters from darkest to lightest. 
                                   Defaults to None.
            width (int, optional): Width of output ASCII art. Defaults to 100.
            height (int, optional): Height of output ASCII art. Defaults to None.
            mode (str, optional): Rendering mode. Options: "standard", "dense", 
                                 "blocks", "braille". Defaults to "standard".
        """
        self.mode = mode
        if chars is not None:
            self.chars = chars
        elif mode == "standard":
            self.chars = self.ASCII_CHARS
        elif mode == "dense":
            self.chars = self.DENSE_CHARS
        elif mode == "blocks":
            self.chars = self.BLOCK_CHARS
        elif mode == "braille":
            self.chars = self.BRAILLE_CHARS
        else:
            self.chars = self.ASCII_CHARS
            
        self.width = width
        self.height = height
        
        # Image enhancement parameters
        self.contrast = 1.0
        self.brightness = 1.0
        self.sharpness = 1.0
        self.dithering = False
        self.edge_enhance = False
        self.invert = False

    def set_enhancement(self, contrast=None, brightness=None, sharpness=None, 
                       dithering=None, edge_enhance=None, invert=None):
        """
        Set image enhancement parameters.
        
        Args:
            contrast (float, optional): Contrast adjustment (1.0 is neutral). 
            brightness (float, optional): Brightness adjustment (1.0 is neutral).
            sharpness (float, optional): Sharpness adjustment (1.0 is neutral).
            dithering (bool, optional): Whether to apply dithering.
            edge_enhance (bool, optional): Whether to enhance edges.
            invert (bool, optional): Whether to invert the image.
        """
        if contrast is not None:
            self.contrast = contrast
        if brightness is not None:
            self.brightness = brightness
        if sharpness is not None:
            self.sharpness = sharpness
        if dithering is not None:
            self.dithering = dithering
        if edge_enhance is not None:
            self.edge_enhance = edge_enhance
        if invert is not None:
            self.invert = invert

    def _resize_image(self, image):
        """
        Resize image to the specified width and height.
        
        Args:
            image (PIL.Image): The image to resize.
            
        Returns:
            PIL.Image: The resized image.
        """
        if self.mode == "braille":
            # For braille, we want 4x the width and 2x the height for proper mapping
            width = self.width * 2
            height = self.height * 4 if self.height else int(image.height * width / image.width / 1.25)
            return image.resize((width, height))
        else:
            width = self.width
            height = self.height or int(image.height * width / image.width / 2.5)
            return image.resize((width, height))

    def _enhance_image(self, image):
        """
        Apply various image enhancements.
        
        Args:
            image (PIL.Image): The image to enhance.
            
        Returns:
            PIL.Image: The enhanced image.
        """
        # Apply contrast adjustment
        if self.contrast != 1.0:
            image = ImageEnhance.Contrast(image).enhance(self.contrast)
        
        # Apply brightness adjustment
        if self.brightness != 1.0:
            image = ImageEnhance.Brightness(image).enhance(self.brightness)
        
        # Apply sharpness adjustment
        if self.sharpness != 1.0:
            image = ImageEnhance.Sharpness(image).enhance(self.sharpness)
        
        # Apply edge enhancement
        if self.edge_enhance:
            image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        # Apply inversion
        if self.invert:
            image = ImageOps.invert(image)
        
        return image

    def _convert_to_grayscale(self, image):
        """
        Convert image to grayscale.
        
        Args:
            image (PIL.Image): The image to convert.
            
        Returns:
            PIL.Image: The grayscale image.
        """
        return image.convert("L")

    def _apply_dithering(self, image):
        """
        Apply Floyd-Steinberg dithering to the image.
        
        Args:
            image (PIL.Image): The grayscale image.
            
        Returns:
            PIL.Image: The dithered image.
        """
        if not self.dithering:
            return image
        
        # For true dithering, we need to use a 1-bit image with dithering
        # But for our ASCII art, we'll simulate it by using PIL's built-in dithering
        return image.convert("1").convert("L")

    def _map_pixels_to_ascii_standard(self, image):
        """
        Map each pixel to an ASCII character using standard mapping.
        
        Args:
            image (PIL.Image): The grayscale image.
            
        Returns:
            list: 2D list of ASCII characters.
        """
        pixels = list(image.getdata())
        width = image.width
        ascii_image = []
        
        # Split the pixel list into rows
        for i in range(0, len(pixels), width):
            row = pixels[i:i + width]
            ascii_row = []
            
            for pixel in row:
                # Map pixel value (0-255) to an index in our ASCII characters list
                index = int(pixel * (len(self.chars) - 1) / 255)
                ascii_row.append(self.chars[index])
            
            ascii_image.append(ascii_row)
        
        return ascii_image

    def _map_pixels_to_ascii_braille(self, image):
        """
        Map pixels to braille characters (each braille character represents a 2x4 grid).
        
        Args:
            image (PIL.Image): The grayscale image.
            
        Returns:
            list: 2D list of braille characters.
        """
        pixels = np.array(image)
        height, width = pixels.shape
        
        # Calculate output dimensions
        out_height = height // 4
        out_width = width // 2
        
        ascii_image = []
        
        # Process 2x4 blocks of pixels
        for y in range(0, out_height):
            ascii_row = []
            for x in range(0, out_width):
                # Extract 2x4 block
                block = pixels[y*4:y*4+4, x*2:x*2+2]
                
                # Convert to binary (threshold at 128)
                binary_block = (block < 128).flatten()
                
                # Calculate braille pattern
                # Braille dot pattern:
                # 0 3
                # 1 4
                # 2 5
                # 6 7
                pattern = 0
                for i, bit in enumerate(binary_block):
                    if bit:
                        if i < 6:
                            pattern |= (1 << i)
                        else:
                            # Positions 6 and 7 are mapped to bits 6 and 7 in Unicode
                            pattern |= (1 << (i + 2))
                
                # Map to corresponding braille character
                braille_char = chr(0x2800 + pattern)
                ascii_row.append(braille_char)
            
            ascii_image.append(ascii_row)
        
        return ascii_image

    def _map_pixels_to_ascii(self, image):
        """
        Map pixels to ASCII characters based on the selected mode.
        
        Args:
            image (PIL.Image): The grayscale image.
            
        Returns:
            list: 2D list of characters.
        """
        if self.mode == "braille":
            return self._map_pixels_to_ascii_braille(image)
        else:
            return self._map_pixels_to_ascii_standard(image)

    def generate_from_image(self, image_path):
        """
        Generate ASCII art from an image file.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            str: ASCII art as a string.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Error opening image: {e}")
        
        # Process the image
        image = self._resize_image(image)
        image = self._enhance_image(image)
        grayscale_image = self._convert_to_grayscale(image)
        
        if self.dithering:
            grayscale_image = self._apply_dithering(grayscale_image)
        
        ascii_image = self._map_pixels_to_ascii(grayscale_image)
        
        # Convert 2D list to string
        return "\n".join("".join(row) for row in ascii_image)

    def generate_from_pil_image(self, image):
        """
        Generate ASCII art from a PIL Image object.
        
        Args:
            image (PIL.Image): PIL Image object.
            
        Returns:
            str: ASCII art as a string.
        """
        # Process the image
        image = self._resize_image(image)
        image = self._enhance_image(image)
        grayscale_image = self._convert_to_grayscale(image)
        
        if self.dithering:
            grayscale_image = self._apply_dithering(grayscale_image)
        
        ascii_image = self._map_pixels_to_ascii(grayscale_image)
        
        # Convert 2D list to string
        return "\n".join("".join(row) for row in ascii_image)

    def generate_html(self, image_path, font_size=10, font_family="monospace", 
                     preserve_color=False):
        """
        Generate HTML representation of the ASCII art with optional color.
        
        Args:
            image_path (str): Path to the image file.
            font_size (int, optional): Font size in pixels. Defaults to 10.
            font_family (str, optional): Font family. Defaults to "monospace".
            preserve_color (bool, optional): Whether to preserve the original colors.
                                          Defaults to False.
        
        Returns:
            str: HTML string representing the ASCII art.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            image = Image.open(image_path)
            original_image = image.copy()
        except Exception as e:
            raise ValueError(f"Error opening image: {e}")
        
        # Process the image for ASCII mapping
        image = self._resize_image(image)
        image = self._enhance_image(image)
        grayscale_image = self._convert_to_grayscale(image)
        
        if self.dithering:
            grayscale_image = self._apply_dithering(grayscale_image)
        
        # Get pixel data
        if preserve_color:
            # Resize the original image to match our processed dimensions
            color_image = self._resize_image(original_image)
            color_pixels = np.array(color_image)
        
        gray_pixels = np.array(grayscale_image)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
<title>ASCII Art</title>
<style>
  pre {{
    font-family: {font_family};
    font-size: {font_size}px;
    line-height: 1;
    letter-spacing: 0;
    background-color: black;
    color: white;
    display: inline-block;
    padding: 10px;
  }}
  span {{ 
    display: inline-block; 
  }}
</style>
</head>
<body>
<pre>
"""
        
        # Map pixels to ASCII
        height, width = gray_pixels.shape
        
        for y in range(height):
            for x in range(width):
                pixel_value = gray_pixels[y, x]
                index = int(pixel_value * (len(self.chars) - 1) / 255)
                char = self.chars[index]
                
                if preserve_color and len(color_pixels.shape) > 2:
                    # Get the RGB color for this pixel
                    r, g, b = color_pixels[y, x][:3]
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    html += f'<span style="color:{color}">{char}</span>'
                else:
                    html += char
            
            html += '\n'
        
        html += """</pre>
</body>
</html>"""
        
        return html

    def save_to_file(self, ascii_art, output_path):
        """
        Save ASCII art to a file.
        
        Args:
            ascii_art (str): The ASCII art to save.
            output_path (str): Path to save the ASCII art.
        """
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(ascii_art)

    def save_html_to_file(self, html, output_path):
        """
        Save HTML to a file.
        
        Args:
            html (str): The HTML to save.
            output_path (str): Path to save the HTML.
        """
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html)


# Convenience functions
def image_to_enhanced_ascii(image_path, width=100, height=None, mode="standard", 
                          contrast=1.0, brightness=1.0, sharpness=1.0, 
                          dithering=False, edge_enhance=False, invert=False):
    """
    Convenience function to convert an image to enhanced ASCII art.
    
    Args:
        image_path (str): Path to the image file.
        width (int, optional): Width of output ASCII art. Defaults to 100.
        height (int, optional): Height of output ASCII art. Defaults to None.
        mode (str, optional): Rendering mode. Options: "standard", "dense", 
                             "blocks", "braille". Defaults to "standard".
        contrast (float, optional): Contrast adjustment (1.0 is neutral).
        brightness (float, optional): Brightness adjustment (1.0 is neutral).
        sharpness (float, optional): Sharpness adjustment (1.0 is neutral).
        dithering (bool, optional): Whether to apply dithering.
        edge_enhance (bool, optional): Whether to enhance edges.
        invert (bool, optional): Whether to invert the image.
        
    Returns:
        str: ASCII art as a string.
    """
    generator = EnhancedAsciiArtGenerator(width=width, height=height, mode=mode)
    generator.set_enhancement(contrast=contrast, brightness=brightness, 
                            sharpness=sharpness, dithering=dithering, 
                            edge_enhance=edge_enhance, invert=invert)
    return generator.generate_from_image(image_path)


def image_to_html_ascii(image_path, width=100, height=None, mode="dense", 
                      preserve_color=True, font_size=8, font_family="monospace",
                      contrast=1.2, brightness=1.0, dithering=False, 
                      edge_enhance=True, invert=False):
    """
    Convenience function to convert an image to HTML ASCII art with color.
    
    Args:
        image_path (str): Path to the image file.
        width (int, optional): Width of output ASCII art. Defaults to 100.
        height (int, optional): Height of output ASCII art. Defaults to None.
        mode (str, optional): Rendering mode. Options: "standard", "dense", 
                             "blocks", "braille". Defaults to "dense".
        preserve_color (bool, optional): Whether to preserve original colors.
        font_size (int, optional): Font size in pixels. Defaults to 8.
        font_family (str, optional): Font family. Defaults to "monospace".
        contrast (float, optional): Contrast adjustment (1.0 is neutral).
        brightness (float, optional): Brightness adjustment (1.0 is neutral).
        dithering (bool, optional): Whether to apply dithering.
        edge_enhance (bool, optional): Whether to enhance edges.
        invert (bool, optional): Whether to invert the image.
        
    Returns:
        str: HTML string representing the ASCII art.
    """
    generator = EnhancedAsciiArtGenerator(width=width, height=height, mode=mode)
    generator.set_enhancement(contrast=contrast, brightness=brightness, 
                            dithering=dithering, edge_enhance=edge_enhance, 
                            invert=invert)
    return generator.generate_html(image_path, font_size=font_size, 
                                  font_family=font_family, 
                                  preserve_color=preserve_color) 