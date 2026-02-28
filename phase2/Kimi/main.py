#!/usr/bin/env python3
"""
Voronoi Diagram Generator - Main Entry Point.

This application generates Voronoi diagrams from a set of input points.
It provides both a command-line interface and a graphical user interface.

Usage:
    python main.py                    # Launch GUI
    python main.py --gui              # Launch GUI (explicit)
    python main.py --input points.txt # Generate and save diagram
    python main.py --help             # Show help

Examples:
    # Launch GUI
    python main.py

    # Generate SVG from points file
    python main.py --input examples/points.txt --output diagram.svg

    # Generate PNG image
    python main.py --input examples/points.txt --output diagram.png
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.file_parser import PointFileParser, FileParserError
from src.voronoi_calculator import VoronoiCalculator
from src.exporters import ExporterFactory, ExportError


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate Voronoi diagrams from point data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Launch GUI
  %(prog)s --gui                     # Launch GUI (explicit)
  %(prog)s -i points.txt -o out.svg  # Generate SVG
  %(prog)s -i points.txt -o out.png  # Generate PNG image
        """
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface (default if no other options)"
    )
    
    parser.add_argument(
        "-i", "--input",
        metavar="FILE",
        help="Input file containing points (x,y format, one per line)"
    )
    
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Output file for the diagram (SVG or image format)"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Output width in pixels (default: 800)"
    )
    
    parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="Output height in pixels (default: 600)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def generate_diagram(
    input_path: str,
    output_path: str,
    width: int = 800,
    height: int = 600
) -> bool:
    """
    Generate a Voronoi diagram from input file and save to output.
    
    Args:
        input_path: Path to the input points file.
        output_path: Path to the output file.
        width: Output width in pixels.
        height: Output height in pixels.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Parse input file
        print(f"Reading points from: {input_path}")
        parser = PointFileParser()
        points = parser.parse(input_path)
        print(f"Loaded {len(points)} points")
        
        # Generate Voronoi diagram
        print("Computing Voronoi diagram...")
        calculator = VoronoiCalculator()
        diagram = calculator.calculate(points)
        print(f"Generated {len(diagram.cells)} cells")
        
        # Export to file
        print(f"Exporting to: {output_path}")
        exporter = ExporterFactory.create_exporter(output_path)
        
        # Configure exporter dimensions if applicable
        if hasattr(exporter, '_width'):
            exporter._width = width
        if hasattr(exporter, '_height'):
            exporter._height = height
        
        exporter.export(diagram, output_path)
        print("Done!")
        return True
        
    except FileParserError as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return False
    except ExportError as e:
        print(f"Error exporting diagram: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def launch_gui() -> None:
    """Launch the graphical user interface."""
    try:
        from src.gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error launching GUI: {e}", file=sys.stderr)
        print("Make sure tkinter is installed.", file=sys.stderr)
        sys.exit(1)


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).
        
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_argument_parser()
    args = parser.parse_args(argv)
    
    # If no arguments provided, launch GUI
    if len(sys.argv) == 1:
        launch_gui()
        return 0
    
    # If --gui flag is set, launch GUI
    if args.gui:
        launch_gui()
        return 0
    
    # If input file provided, process it
    if args.input:
        if not args.output:
            print("Error: --output is required when using --input", file=sys.stderr)
            return 1
        
        success = generate_diagram(
            args.input,
            args.output,
            args.width,
            args.height
        )
        return 0 if success else 1
    
    # Default: launch GUI
    launch_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
