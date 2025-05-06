#!/usr/bin/env python3
"""
Example script demonstrating basic usage of the ashiart package.
"""

import os
import sys
from PIL import Image, ImageDraw

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ashiart import AsciiArtGenerator, image_to_ascii


def create_test_image(filename, size=(200, 100)):
    """Create a simple test image."""
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)
    
    # Draw a black rectangle on the left half
    draw.rectangle([(0, 0), (size[0] // 2, size[1])], fill="black")
    
    # Draw a gray rectangle on the top right quadrant
    draw.rectangle([(size[0] // 2, 0), (size[0], size[1] // 2)], fill="gray")
    
    # Save the image
    image.save(filename)
    print(f"Created test image: {filename}")
    return filename


def main():
    """Run the example."""
    # Create a test image if none is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "test_image.png"
        create_test_image(image_path)
    
    print("\n=== Using the convenience function ===")
    ascii_art = image_to_ascii(image_path, width=60)
    print(ascii_art)
    
    print("\n=== Using the AsciiArtGenerator class ===")
    generator = AsciiArtGenerator(width=40)
    ascii_art = generator.generate_from_image(image_path)
    print(ascii_art)
    
    print("\n=== Using custom ASCII characters ===")
    custom_chars = ["#", "@", "O", "o", ".", " "]
    generator = AsciiArtGenerator(chars=custom_chars, width=40)
    ascii_art = generator.generate_from_image(image_path)
    print(ascii_art)
    
    # Save to file
    output_file = "output.txt"
    generator.save_to_file(ascii_art, output_file)
    print(f"\nASCII art saved to {output_file}")


if __name__ == "__main__":
    main() 