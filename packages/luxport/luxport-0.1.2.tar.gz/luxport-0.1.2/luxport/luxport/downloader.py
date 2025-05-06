"""
Handles downloading IIIF manifests and associated images
"""

import os
import json
import requests
from tqdm import tqdm
from typing import Dict, Any, List, Optional, Tuple

class ManifestDownloader:
    """Downloads IIIF manifests and their associated images"""
    
    def __init__(self, manifest_url: str = None, manifest_data: Dict = None):
        """
        Initialize with either a manifest URL or manifest data.
        
        Args:
            manifest_url: URL to an IIIF manifest
            manifest_data: Already loaded manifest data as a dictionary
        """
        self.manifest_url = manifest_url
        self._manifest_data = manifest_data
        self._session = requests.Session()
    
    def download_manifest(self) -> Dict[str, Any]:
        """
        Download and parse the manifest JSON.
        
        Returns:
            dict: The parsed manifest data
        """
        if self._manifest_data:
            return self._manifest_data
            
        if not self.manifest_url:
            raise ValueError("No manifest URL provided")
            
        response = self._session.get(self.manifest_url)
        response.raise_for_status()
        
        self._manifest_data = response.json()
        return self._manifest_data
    
    def get_manifest_id(self) -> str:
        """
        Extract the manifest ID from the manifest data or URL.
        
        Returns:
            str: The manifest ID
        """
        manifest = self.download_manifest()
        
        if 'id' in manifest:
            # Extract the ID from the end of the URL
            return manifest['id'].split('/')[-1]
        
        # Fallback to extracting from the manifest URL
        if self.manifest_url:
            return self.manifest_url.split('/')[-1]
            
        return "unknown"
    
    def get_images(self) -> List[Dict[str, Any]]:
        """
        Extract all image information from the manifest.
        
        Returns:
            list: List of image info dictionaries
        """
        manifest = self.download_manifest()
        images = []
        
        if 'items' not in manifest:
            return images
            
        for canvas in manifest['items']:
            if canvas.get('type') == 'Canvas' and 'items' in canvas:
                for annotation_page in canvas['items']:
                    if 'items' in annotation_page:
                        for annotation in annotation_page['items']:
                            if annotation.get('motivation') == 'painting' and 'body' in annotation:
                                body = annotation['body']
                                
                                if body.get('type') == 'Image' and 'id' in body:
                                    # Add full image
                                    image_info = {
                                        'id': body['id'],
                                        'canvas_id': canvas.get('id', ''),
                                        'label': canvas.get('label', {}).get('none', ['Unknown'])[0],
                                        'height': body.get('height'),
                                        'width': body.get('width'),
                                        'format': body.get('format', 'image/jpeg'),
                                        'type': 'full'
                                    }
                                    images.append(image_info)
            
            # Look for thumbnails
            if 'thumbnail' in canvas:
                for thumb in canvas['thumbnail']:
                    if thumb.get('type') == 'Image' and 'id' in thumb:
                        thumb_info = {
                            'id': thumb['id'],
                            'canvas_id': canvas.get('id', ''),
                            'label': canvas.get('label', {}).get('none', ['Unknown'])[0],
                            'height': thumb.get('height'),
                            'width': thumb.get('width'),
                            'format': thumb.get('format', 'image/jpeg'),
                            'type': 'thumbnail'
                        }
                        images.append(thumb_info)
        
        return images
    
    def download_image(self, image_url: str, output_path: str) -> bool:
        """
        Download a single image to the specified path.
        
        Args:
            image_url: URL of the image to download
            output_path: Local path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self._session.get(image_url, stream=True)
            response.raise_for_status()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the image
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return True
        except Exception as e:
            print(f"Error downloading {image_url}: {str(e)}")
            return False
    
    def download_all_images(self, output_dir: str, progress: bool = True) -> Tuple[int, int]:
        """
        Download all images from the manifest to the specified directory.
        
        Args:
            output_dir: Directory to save images
            progress: Whether to show a progress bar
            
        Returns:
            tuple: (number of successful downloads, total number of images)
        """
        images = self.get_images()
        successful = 0
        
        # Create output directories
        full_dir = os.path.join(output_dir, 'images', 'full')
        thumb_dir = os.path.join(output_dir, 'images', 'thumbnails')
        os.makedirs(full_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)
        
        # Download images with progress bar
        iterator = tqdm(images, desc="Downloading images") if progress else images
        
        for img in iterator:
            # Extract the image ID from the URL
            if '/iiif/' in img['id']:
                # Format: https://collections.library.yale.edu/iiif/2/16868023/full/full/0/default.jpg
                parts = img['id'].split('/')
                for i, part in enumerate(parts):
                    if part == 'iiif' and i+1 < len(parts):
                        img_id = parts[i+2]  # Get the ID after 'iiif/2/'
                        break
                else:
                    img_id = img['id'].split('/')[-2]  # Fallback
            elif '/canvas/' in img['canvas_id']:
                # Extract from canvas ID if image ID doesn't have the info
                img_id = img['canvas_id'].split('/')[-1]
            else:
                # Last fallback - use a hash of the URL
                img_id = img['id'].split('/')[-1].split('.')[0]
                if not img_id or img_id == 'default':
                    img_id = img['id'].replace('/', '_').replace(':', '')[-30:]
            
            # Get file extension from format or URL
            if '.' in img['id'] and img['id'].split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif']:
                extension = img['id'].split('.')[-1].lower()
            else:
                extension = img['format'].split('/')[-1] if img.get('format') else 'jpg'
                if extension not in ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif']:
                    extension = 'jpg'  # Default to jpg if unknown format
            
            # Set output path based on image type
            if img['type'] == 'full':
                output_path = os.path.join(full_dir, f"{img_id}.{extension}")
            else:
                output_path = os.path.join(thumb_dir, f"{img_id}.{extension}")
            
            if self.download_image(img['id'], output_path):
                successful += 1
                
        return successful, len(images) 