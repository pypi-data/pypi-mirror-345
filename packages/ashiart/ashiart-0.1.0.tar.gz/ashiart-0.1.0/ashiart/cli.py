"""Command-line interface for ASCII art generator."""

import argparse
import sys
from .generator import AsciiArtGenerator


def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument(
        "-o", "--output", 
        help="Path to save the ASCII art output (if not provided, prints to console)"
    )
    parser.add_argument(
        "-w", "--width", 
        type=int, 
        default=100, 
        help="Width of the ASCII art in characters (default: 100)"
    )
    parser.add_argument(
        "-H", "--height", 
        type=int, 
        help="Height of the ASCII art in characters (defaults to proportional height)"
    )
    parser.add_argument(
        "-c", "--chars", 
        help="Custom ASCII characters from darkest to lightest (e.g. '@#$%*+;:,.')"
    )
    
    args = parser.parse_args()
    
    # Create generator with custom parameters
    chars = list(args.chars) if args.chars else None
    generator = AsciiArtGenerator(
        chars=chars,
        width=args.width,
        height=args.height
    )
    
    try:
        # Generate ASCII art
        ascii_art = generator.generate_from_image(args.image_path)
        
        # Output the result
        if args.output:
            generator.save_to_file(ascii_art, args.output)
            print(f"ASCII art saved to {args.output}")
        else:
            print(ascii_art)
        
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 