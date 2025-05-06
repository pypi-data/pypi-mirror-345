"""Tests for the enhanced ASCII art generator module."""

import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image, ImageDraw

from ashiart.enhanced import EnhancedAsciiArtGenerator, image_to_enhanced_ascii, image_to_html_ascii


class TestEnhancedAsciiArtGenerator(unittest.TestCase):
    """Test the EnhancedAsciiArtGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = EnhancedAsciiArtGenerator(width=10, height=5)
        
        # Create a test image
        self.test_image = Image.new("RGB", (100, 50), color="white")
        draw = ImageDraw.Draw(self.test_image)
        draw.rectangle([(0, 0), (50, 25)], fill="black")
        
        # Create temp file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.png")
        self.test_image.save(self.test_image_path)
        
        # Output paths for saving tests
        self.output_path = os.path.join(self.temp_dir.name, "output.txt")
        self.html_output_path = os.path.join(self.temp_dir.name, "output.html")

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_init_modes(self):
        """Test initialization with different modes."""
        # Standard mode
        self.assertEqual(self.generator.chars, EnhancedAsciiArtGenerator.ASCII_CHARS)
        
        # Dense mode
        dense_generator = EnhancedAsciiArtGenerator(mode="dense")
        self.assertEqual(dense_generator.chars, EnhancedAsciiArtGenerator.DENSE_CHARS)
        
        # Blocks mode
        blocks_generator = EnhancedAsciiArtGenerator(mode="blocks")
        self.assertEqual(blocks_generator.chars, EnhancedAsciiArtGenerator.BLOCK_CHARS)
        
        # Braille mode
        braille_generator = EnhancedAsciiArtGenerator(mode="braille")
        self.assertEqual(braille_generator.chars, EnhancedAsciiArtGenerator.BRAILLE_CHARS)
        
        # Custom chars
        custom_chars = ["X", "O", "."]
        custom_generator = EnhancedAsciiArtGenerator(chars=custom_chars)
        self.assertEqual(custom_generator.chars, custom_chars)

    def test_enhancement_settings(self):
        """Test setting enhancement parameters."""
        # Default values
        self.assertEqual(self.generator.contrast, 1.0)
        self.assertEqual(self.generator.brightness, 1.0)
        self.assertEqual(self.generator.sharpness, 1.0)
        self.assertEqual(self.generator.dithering, False)
        self.assertEqual(self.generator.edge_enhance, False)
        self.assertEqual(self.generator.invert, False)
        
        # Set values
        self.generator.set_enhancement(
            contrast=1.5,
            brightness=0.8,
            sharpness=1.2,
            dithering=True,
            edge_enhance=True,
            invert=True
        )
        
        # Check values were set
        self.assertEqual(self.generator.contrast, 1.5)
        self.assertEqual(self.generator.brightness, 0.8)
        self.assertEqual(self.generator.sharpness, 1.2)
        self.assertEqual(self.generator.dithering, True)
        self.assertEqual(self.generator.edge_enhance, True)
        self.assertEqual(self.generator.invert, True)

    def test_braille_mapping(self):
        """Test braille character mapping."""
        # Only test if we have a compatible environment
        try:
            import numpy as np
            
            # Create a simple binary image for braille mapping
            img = Image.new("L", (2, 4), color=255)  # White
            # Set specific pixels to black (value < 128)
            pixels = [
                [0, 255],  # Top row: left dot set, right not
                [255, 0],  # Second row: left not, right set
                [0, 0],    # Third row: both set
                [255, 255] # Bottom row: none set
            ]
            img = Image.fromarray(np.array(pixels, dtype=np.uint8))
            
            # Create a braille generator with specific width for this test
            braille_generator = EnhancedAsciiArtGenerator(width=1, mode="braille")
            
            # Generate ASCII art
            result = braille_generator._map_pixels_to_ascii_braille(img)
            
            # The pattern should have dots at positions 0, 4, 2, 5
            # In Unicode braille, this corresponds to dots 1, 5, 3, 6
            # Verify we get a single character result with the correct pattern
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 1)
            
            # The exact character code will depend on the braille encoding
            # but we can check it's not the empty braille character
            self.assertNotEqual(result[0][0], chr(0x2800))
            
        except (ImportError, AttributeError):
            self.skipTest("Numpy or PIL features not available for this test.")

    def test_generate_from_image(self):
        """Test generating ASCII art from an image file."""
        ascii_art = self.generator.generate_from_image(self.test_image_path)
        
        # Check that we get a string with the expected dimensions
        lines = ascii_art.strip().split("\n")
        self.assertEqual(len(lines), 5)  # 5 rows
        self.assertEqual(len(lines[0]), 10)  # 10 columns

    def test_html_generation(self):
        """Test HTML generation."""
        html = self.generator.generate_html(
            self.test_image_path,
            preserve_color=True,
            font_size=8
        )
        
        # Check for HTML structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<style>", html)
        self.assertIn("<pre>", html)
        
        # Save HTML to a file
        self.generator.save_html_to_file(html, self.html_output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.html_output_path))
        
        # Check file content
        with open(self.html_output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertEqual(content, html)

    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test image_to_enhanced_ascii
        ascii_art = image_to_enhanced_ascii(
            self.test_image_path,
            width=10,
            mode="dense",
            contrast=1.2
        )
        
        # Check that we get a string
        self.assertIsInstance(ascii_art, str)
        
        # Test image_to_html_ascii
        html = image_to_html_ascii(
            self.test_image_path,
            width=10,
            preserve_color=True
        )
        
        # Check that we get a string with HTML
        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)


if __name__ == "__main__":
    unittest.main() 