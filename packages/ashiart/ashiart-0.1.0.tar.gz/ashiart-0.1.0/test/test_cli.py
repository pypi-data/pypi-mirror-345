"""Tests for the ASCII art generator CLI."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
from PIL import Image

from ashiart.cli import main


class TestCLI(unittest.TestCase):
    """Test the command-line interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test image
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.png")
        self.output_path = os.path.join(self.temp_dir.name, "output.txt")
        
        # Create a simple test image
        test_image = Image.new("RGB", (10, 10), color="white")
        test_image.save(self.test_image_path)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_with_output_file(self, mock_print, mock_argv):
        """Test CLI with output to file."""
        # Mock the command-line arguments
        mock_argv.__getitem__.side_effect = lambda i: [
            "ashiart", 
            self.test_image_path, 
            "-o", self.output_path,
            "-w", "5",
            "-H", "3"
        ][i]
        mock_argv.__len__.return_value = 7
        
        # Run the CLI
        result = main()
        
        # Check that the function completed successfully
        self.assertEqual(result, 0)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(self.output_path))
        
        # Check that the success message was printed
        mock_print.assert_called_with(f"ASCII art saved to {self.output_path}")

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_with_console_output(self, mock_print, mock_argv):
        """Test CLI with output to console."""
        # Mock the command-line arguments
        mock_argv.__getitem__.side_effect = lambda i: [
            "ashiart", 
            self.test_image_path, 
            "-w", "5",
            "-H", "3"
        ][i]
        mock_argv.__len__.return_value = 5
        
        # Run the CLI
        result = main()
        
        # Check that the function completed successfully
        self.assertEqual(result, 0)
        
        # Check that something was printed (the ASCII art)
        mock_print.assert_called()

    @patch('sys.argv')
    def test_main_with_nonexistent_file(self, mock_argv):
        """Test CLI with a non-existent file."""
        # Mock the command-line arguments
        mock_argv.__getitem__.side_effect = lambda i: [
            "ashiart", 
            "nonexistent_file.jpg"
        ][i]
        mock_argv.__len__.return_value = 2
        
        # Run the CLI and check for error exit code
        with patch('builtins.print') as mock_print:
            result = main()
            self.assertEqual(result, 1)
            
            # Check that an error message was printed
            mock_print.assert_called()


if __name__ == "__main__":
    unittest.main() 