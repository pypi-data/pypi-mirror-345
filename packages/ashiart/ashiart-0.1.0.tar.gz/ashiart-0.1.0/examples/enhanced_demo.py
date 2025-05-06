#!/usr/bin/env python3
"""
Demonstration script for the enhanced ASCII art generator.
Shows various rendering modes and enhancement options.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path to import the package directly from source
# (not needed if the package is installed)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ashiart import EnhancedAsciiArtGenerator, image_to_html_ascii


def create_output_directory():
    """Create the output directory if it doesn't exist."""
    output_dir = Path("demo_outputs")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_standard_enhancements(image_path, output_dir):
    """Demonstrate standard mode with various enhancements."""
    print("Generating standard mode examples with various enhancements...")
    
    # Basic output
    generator = EnhancedAsciiArtGenerator(width=80, mode="standard")
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_standard.txt"
    generator.save_to_file(ascii_art, output_path)
    
    # Higher contrast
    generator.set_enhancement(contrast=1.8)
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_standard_contrast.txt"
    generator.save_to_file(ascii_art, output_path)
    
    # Edge enhancement
    generator.set_enhancement(contrast=1.2, edge_enhance=True)
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_standard_edge.txt"
    generator.save_to_file(ascii_art, output_path)
    
    # Dithering
    generator.set_enhancement(contrast=1.0, edge_enhance=False, dithering=True)
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_standard_dither.txt"
    generator.save_to_file(ascii_art, output_path)


def demo_rendering_modes(image_path, output_dir):
    """Demonstrate different rendering modes."""
    print("Generating examples with different rendering modes...")
    
    # Dense character set
    generator = EnhancedAsciiArtGenerator(width=80, mode="dense")
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_dense.txt"
    generator.save_to_file(ascii_art, output_path)
    
    # Block characters
    generator = EnhancedAsciiArtGenerator(width=80, mode="blocks")
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_blocks.txt"
    generator.save_to_file(ascii_art, output_path)
    
    # Braille patterns
    generator = EnhancedAsciiArtGenerator(width=40, mode="braille")
    ascii_art = generator.generate_from_image(image_path)
    output_path = output_dir / "demo_braille.txt"
    generator.save_to_file(ascii_art, output_path)


def demo_html_outputs(image_path, output_dir):
    """Demonstrate HTML outputs with color preservation."""
    print("Generating HTML examples with color preservation...")
    
    # Dense mode with color
    generator = EnhancedAsciiArtGenerator(width=80, mode="dense")
    generator.set_enhancement(contrast=1.2, edge_enhance=True)
    html = generator.generate_html(image_path, preserve_color=True, font_size=8)
    output_path = output_dir / "demo_color_dense.html"
    generator.save_html_to_file(html, output_path)
    
    # Braille mode with color
    generator = EnhancedAsciiArtGenerator(width=40, mode="braille")
    html = generator.generate_html(image_path, preserve_color=True, font_size=10)
    output_path = output_dir / "demo_color_braille.html"
    generator.save_html_to_file(html, output_path)
    
    # Block mode with color
    generator = EnhancedAsciiArtGenerator(width=80, mode="blocks")
    html = generator.generate_html(image_path, preserve_color=True, font_size=8)
    output_path = output_dir / "demo_color_blocks.html"
    generator.save_html_to_file(html, output_path)
    
    # HTML using the convenience function
    html = image_to_html_ascii(
        image_path,
        width=80,
        preserve_color=True,
        contrast=1.3,
        edge_enhance=True
    )
    output_path = output_dir / "demo_color_enhanced.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description="Demonstrate enhanced ASCII art generation")
    parser.add_argument("image", help="Path to the image file")
    args = parser.parse_args()
    
    image_path = args.image
    
    # Check if the file exists
    if not os.path.isfile(image_path):
        print(f"Error: Image file '{image_path}' not found")
        return 1
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"Outputs will be saved to: {output_dir.absolute()}")
    
    # Run demos
    demo_standard_enhancements(image_path, output_dir)
    demo_rendering_modes(image_path, output_dir)
    demo_html_outputs(image_path, output_dir)
    
    print("\nAll demos completed successfully!")
    print(f"Check the output files in the '{output_dir}' directory")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 