"""ASCII Art Generator module."""

import os
from PIL import Image


class AsciiArtGenerator:
    """A class to generate ASCII art from images."""

    # ASCII characters from darkest to lightest
    ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

    def __init__(self, chars=None, width=100, height=None):
        """
        Initialize the ASCII art generator.
        
        Args:
            chars (list, optional): ASCII characters from darkest to lightest. 
                                   Defaults to None.
            width (int, optional): Width of output ASCII art. Defaults to 100.
            height (int, optional): Height of output ASCII art. Defaults to None.
        """
        self.chars = chars or self.ASCII_CHARS
        self.width = width
        self.height = height

    def _resize_image(self, image):
        """
        Resize image to the specified width and height.
        
        Args:
            image (PIL.Image): The image to resize.
            
        Returns:
            PIL.Image: The resized image.
        """
        width = self.width
        height = self.height or int(image.height * width / image.width / 2.5)
        return image.resize((width, height))

    def _convert_to_grayscale(self, image):
        """
        Convert image to grayscale.
        
        Args:
            image (PIL.Image): The image to convert.
            
        Returns:
            PIL.Image: The grayscale image.
        """
        return image.convert("L")

    def _map_pixels_to_ascii(self, image):
        """
        Map each pixel to an ASCII character.
        
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
        grayscale_image = self._convert_to_grayscale(image)
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
        grayscale_image = self._convert_to_grayscale(image)
        ascii_image = self._map_pixels_to_ascii(grayscale_image)
        
        # Convert 2D list to string
        return "\n".join("".join(row) for row in ascii_image)

    def save_to_file(self, ascii_art, output_path):
        """
        Save ASCII art to a file.
        
        Args:
            ascii_art (str): The ASCII art to save.
            output_path (str): Path to save the ASCII art.
        """
        with open(output_path, "w") as file:
            file.write(ascii_art)


def image_to_ascii(image_path, width=100, height=None, chars=None):
    """
    Convenience function to convert an image to ASCII art.
    
    Args:
        image_path (str): Path to the image file.
        width (int, optional): Width of output ASCII art. Defaults to 100.
        height (int, optional): Height of output ASCII art. Defaults to None.
        chars (list, optional): ASCII characters from darkest to lightest. 
                               Defaults to None.
        
    Returns:
        str: ASCII art as a string.
    """
    generator = AsciiArtGenerator(chars=chars, width=width, height=height)
    return generator.generate_from_image(image_path) 