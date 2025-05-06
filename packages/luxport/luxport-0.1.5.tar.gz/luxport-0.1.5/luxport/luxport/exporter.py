"""
Handles exporting IIIF manifest data to ZIP files or directories
"""

import os
import json
import zipfile
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple

from .downloader import ManifestDownloader
from .utils import simplify_manifest, generate_metadata_text, generate_export_info

class ManifestExporter:
    """Exports IIIF manifest data to ZIP files or directories"""
    
    def __init__(self, manifest_url: str = None, manifest_data: Dict = None, format: str = "lux"):
        """
        Initialize with either a manifest URL or manifest data.
        
        Args:
            manifest_url: URL to an IIIF manifest, or a Lux/Linked Art URL
            manifest_data: Already loaded manifest data as a dictionary
            format: Format to use when processing Lux/Linked Art URLs ('lux' or 'la')
        """
        self.downloader = ManifestDownloader(manifest_url, manifest_data, format=format)
    
    def export(self, output_file: str, show_progress: bool = True) -> str:
        """
        Export the manifest data and images to a ZIP file.
        
        Args:
            output_file: Path to the output ZIP file
            show_progress: Whether to show progress bars
            
        Returns:
            str: Path to the created ZIP file
        """
        # Create a temporary directory for the export
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export to the temporary directory
            self.export_to_directory(temp_dir, show_progress)
            
            # Create the ZIP file
            self._create_zip(temp_dir, output_file)
            
        return output_file
    
    def export_to_directory(self, output_dir: str, show_progress: bool = True) -> str:
        """
        Export the manifest data and images to a directory.
        
        Args:
            output_dir: Directory to save the exported data
            show_progress: Whether to show progress bars
            
        Returns:
            str: Path to the export directory
        """
        # Make sure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Download the manifest
        manifest = self.downloader.download_manifest()
        manifest_id = self.downloader.get_manifest_id()
        
        # Save the original manifest JSON
        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Create and save the simplified manifest
        simplified = simplify_manifest(manifest)
        simplified_path = os.path.join(output_dir, "manifest_simplified.json")
        with open(simplified_path, "w", encoding="utf-8") as f:
            json.dump(simplified, f, indent=2, ensure_ascii=False)
        
        # Generate and save metadata text
        metadata_text = generate_metadata_text(manifest)
        metadata_path = os.path.join(output_dir, "metadata.txt")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(metadata_text)
        
        # Download all images
        success, total = self.downloader.download_all_images(output_dir, show_progress)
        
        # Generate and save export info
        info_text = generate_export_info(
            self.downloader.manifest_url, 
            manifest_id,
            total
        )
        info_path = os.path.join(output_dir, "info.txt")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(info_text)
        
        return output_dir
    
    def _create_zip(self, source_dir: str, output_file: str) -> None:
        """
        Create a ZIP file from a directory.
        
        Args:
            source_dir: Directory to compress
            output_file: Path to the output ZIP file
        """
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname) 