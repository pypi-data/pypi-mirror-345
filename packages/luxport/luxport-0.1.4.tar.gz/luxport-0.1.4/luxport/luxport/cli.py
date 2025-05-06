"""
Command-line interface for LuxPort
"""

import os
import sys
import argparse
from typing import List, Optional

from .exporter import ManifestExporter
from .__init__ import __version__

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments to parse
        
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="LuxPort: IIIF Manifest Export Utility",
        prog="luxport"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a manifest to a ZIP file or directory")
    export_parser.add_argument(
        "manifest_url", 
        help="URL of the IIIF manifest to export, or a Lux/Linked Art URL"
    )
    export_parser.add_argument(
        "--output-file", "-o",
        help="Path to the output ZIP file (default: manifest_ID.zip)"
    )
    export_parser.add_argument(
        "--output-dir", "-d",
        help="Path to the output directory (if specified, will not create a ZIP file)"
    )
    export_parser.add_argument(
        "--no-progress", "-n",
        action="store_true",
        help="Disable progress bars"
    )
    export_parser.add_argument(
        "--format", "-f",
        choices=["lux", "la"],
        default="lux",
        help="Format to use when processing Lux/Linked Art URLs ('lux' or 'la')"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments to parse
        
    Returns:
        int: Exit code
    """
    parsed_args = parse_args(args)
    
    # Handle version command
    if parsed_args.command == "version":
        print(f"LuxPort version {__version__}")
        return 0
    
    # Handle export command
    if parsed_args.command == "export":
        try:
            exporter = ManifestExporter(parsed_args.manifest_url, format=parsed_args.format)
            manifest_id = exporter.downloader.get_manifest_id()
            
            # Export to directory if specified
            if parsed_args.output_dir:
                output_dir = parsed_args.output_dir
                exporter.export_to_directory(output_dir, not parsed_args.no_progress)
                print(f"Successfully exported manifest to directory: {output_dir}")
                return 0
            
            # Otherwise export to ZIP file
            output_file = parsed_args.output_file
            if not output_file:
                output_file = f"manifest_{manifest_id}.zip"
            
            exporter.export(output_file, not parsed_args.no_progress)
            print(f"Successfully exported manifest to: {output_file}")
            return 0
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    # No command specified
    if not parsed_args.command:
        print("Error: No command specified. Use 'luxport --help' for usage information.", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 