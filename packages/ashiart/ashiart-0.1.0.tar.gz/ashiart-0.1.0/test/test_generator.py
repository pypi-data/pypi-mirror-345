"""Tests for the ASCII art generator module."""

import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
import tempfile

from ashiart.generator import AsciiArtGenerator, image_to_ascii


class TestAsciiArtGenerator(unittest.TestCase):
    """Test the AsciiArtGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = AsciiArtGenerator(width=10, height=5)
        
        # Create a test image
        self.test_image = Image.new("RGB", (100, 50), color="white")
        draw = ImageDraw.Draw(self.test_image)
        draw.rectangle([(0, 0), (50, 25)], fill="black")
        
        # Create temp file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.png")
        self.test_image.save(self.test_image_path)
        
        # Output path for saving tests
        self.output_path = os.path.join(self.temp_dir.name, "output.txt")

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_init(self):
        """Test initialization with default and custom values."""
        # Default ASCII characters
        self.assertEqual(self.generator.chars, AsciiArtGenerator.ASCII_CHARS)
        
        # Custom ASCII characters
        custom_chars = ["X", "O", "."]
        custom_generator = AsciiArtGenerator(chars=custom_chars)
        self.assertEqual(custom_generator.chars, custom_chars)
        
        # Custom dimensions
        self.assertEqual(self.generator.width, 10)
        self.assertEqual(self.generator.height, 5)

    def test_resize_image(self):
        """Test image resizing."""
        resized = self.generator._resize_image(self.test_image)
        self.assertEqual(resized.width, 10)
        self.assertEqual(resized.height, 5)

    def test_convert_to_grayscale(self):
        """Test grayscale conversion."""
        grayscale = self.generator._convert_to_grayscale(self.test_image)
        self.assertEqual(grayscale.mode, "L")

    def test_map_pixels_to_ascii(self):
        """Test pixel to ASCII character mapping."""
        # Create a small test image with a gradient
        test_img = Image.new("L", (2, 2))
        test_img.putdata([0, 128, 255, 64])  # Black, gray, white, dark gray
        
        # Use only 3 ASCII characters for simpler testing
        self.generator.chars = ["@", "O", "."]
        
        ascii_image = self.generator._map_pixels_to_ascii(test_img)
        
        # Check that we get the expected characters
        self.assertEqual(ascii_image[0][0], "@")  # Darkest (0) -> first char
        self.assertEqual(ascii_image[0][1], "O")  # Mid gray (128) -> middle char
        self.assertEqual(ascii_image[1][0], ".")  # White (255) -> last char
        self.assertEqual(ascii_image[1][1], "@")  # Dark gray (64) -> should be closer to first char

    def test_generate_from_image(self):
        """Test generating ASCII art from an image file."""
        ascii_art = self.generator.generate_from_image(self.test_image_path)
        
        # Check that we get a string with the expected dimensions
        lines = ascii_art.strip().split("\n")
        self.assertEqual(len(lines), 5)  # 5 rows
        self.assertEqual(len(lines[0]), 10)  # 10 columns

    def test_generate_from_pil_image(self):
        """Test generating ASCII art from a PIL Image object."""
        ascii_art = self.generator.generate_from_pil_image(self.test_image)
        
        # Check that we get a string with the expected dimensions
        lines = ascii_art.strip().split("\n")
        self.assertEqual(len(lines), 5)  # 5 rows
        self.assertEqual(len(lines[0]), 10)  # 10 columns

    def test_save_to_file(self):
        """Test saving ASCII art to a file."""
        ascii_art = "TEST\nASCII\nART"
        self.generator.save_to_file(ascii_art, self.output_path)
        
        # Check that the file was created with the correct content
        with open(self.output_path, "r") as f:
            content = f.read()
        
        self.assertEqual(content, ascii_art)

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            self.generator.generate_from_image("nonexistent_file.jpg")

    def test_image_to_ascii_function(self):
        """Test the convenience function."""
        ascii_art = image_to_ascii(self.test_image_path, width=10, height=5)
        
        # Check that we get a string with the expected dimensions
        lines = ascii_art.strip().split("\n")
        self.assertEqual(len(lines), 5)  # 5 rows
        self.assertEqual(len(lines[0]), 10)  # 10 columns


if __name__ == "__main__":
    unittest.main() 