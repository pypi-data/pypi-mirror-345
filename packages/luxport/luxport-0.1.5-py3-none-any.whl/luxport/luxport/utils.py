"""
Utility functions for working with IIIF manifests
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Union, Optional

def simplify_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a simplified version of the manifest with only essential information.
    
    Args:
        manifest: The original manifest data
        
    Returns:
        dict: Simplified manifest
    """
    simplified = {
        "id": manifest.get("id"),
        "type": manifest.get("type"),
        "title": _extract_label(manifest.get("label", {})),
        "provider": _extract_provider(manifest.get("provider", [])),
        "description": _extract_description(manifest.get("metadata", [])),
        "images": [],
        "metadata": _simplify_metadata(manifest.get("metadata", [])),
    }
    
    # Extract image information
    if "items" in manifest:
        for canvas in manifest["items"]:
            if canvas.get("type") == "Canvas" and "items" in canvas:
                image_info = _extract_image_info(canvas)
                if image_info:
                    simplified["images"].append(image_info)
    
    return simplified

def _extract_label(label_obj: Dict[str, Any]) -> str:
    """Extract text from label object"""
    if not label_obj:
        return "Unknown"
        
    # Check for 'none' key first (common pattern)
    if "none" in label_obj and label_obj["none"]:
        return label_obj["none"][0]
        
    # Try all language keys
    for lang in label_obj:
        if label_obj[lang] and isinstance(label_obj[lang], list) and label_obj[lang]:
            return label_obj[lang][0]
            
    return "Unknown"

def _extract_provider(providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract provider information"""
    if not providers:
        return {"name": "Unknown"}
        
    provider = providers[0]
    return {
        "name": _extract_label(provider.get("label", {})),
        "id": provider.get("id")
    }

def _extract_description(metadata: List[Dict[str, Any]]) -> str:
    """Extract description from metadata"""
    for item in metadata:
        label = _extract_label(item.get("label", {}))
        if label.lower() in ["description"]:
            return _extract_label(item.get("value", {}))
    return ""

def _simplify_metadata(metadata: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert complex metadata structure to simple key-value pairs"""
    simplified = []
    
    for item in metadata:
        label = _extract_label(item.get("label", {}))
        value = _extract_label(item.get("value", {}))
        
        simplified.append({
            "label": label,
            "value": value
        })
        
    return simplified

def _extract_image_info(canvas: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract image information from a canvas"""
    # Skip canvases without items
    if "items" not in canvas:
        return None
        
    image_info = {
        "id": canvas.get("id"),
        "label": _extract_label(canvas.get("label", {})),
        "height": canvas.get("height"),
        "width": canvas.get("width"),
        "full_image": None,
        "thumbnail": None,
    }
    
    # Find the main image (painting annotation)
    for annotation_page in canvas["items"]:
        if "items" in annotation_page:
            for annotation in annotation_page["items"]:
                if annotation.get("motivation") == "painting" and "body" in annotation:
                    body = annotation["body"]
                    if body.get("type") == "Image" and "id" in body:
                        image_info["full_image"] = {
                            "id": body["id"],
                            "format": body.get("format", "image/jpeg"),
                            "height": body.get("height"),
                            "width": body.get("width"),
                        }
    
    # Find thumbnail
    if "thumbnail" in canvas and canvas["thumbnail"]:
        thumbnail = canvas["thumbnail"][0]
        if "id" in thumbnail:
            image_info["thumbnail"] = {
                "id": thumbnail["id"],
                "format": thumbnail.get("format", "image/jpeg"),
                "height": thumbnail.get("height"),
                "width": thumbnail.get("width"),
            }
    
    return image_info

def generate_metadata_text(manifest: Dict[str, Any]) -> str:
    """
    Generate a human-readable text representation of the manifest metadata.
    
    Args:
        manifest: The manifest data
        
    Returns:
        str: Formatted metadata text
    """
    lines = []
    
    # Add title
    if "label" in manifest:
        title = _extract_label(manifest["label"])
        lines.append(f"TITLE: {title}")
        lines.append("=" * 80)
        lines.append("")
    
    # Add metadata
    if "metadata" in manifest:
        lines.append("METADATA:")
        lines.append("-" * 80)
        
        for item in manifest["metadata"]:
            label = _extract_label(item.get("label", {}))
            value = _extract_label(item.get("value", {}))
            lines.append(f"{label}: {value}")
        
        lines.append("")
    
    # Add provider
    if "provider" in manifest and manifest["provider"]:
        provider = manifest["provider"][0]
        provider_name = _extract_label(provider.get("label", {}))
        lines.append(f"PROVIDER: {provider_name}")
        
        if "homepage" in provider and provider["homepage"]:
            homepage = provider["homepage"][0].get("id", "")
            lines.append(f"HOMEPAGE: {homepage}")
            
        lines.append("")
    
    # Add image summary
    if "items" in manifest:
        image_count = len([i for i in manifest["items"] if i.get("type") == "Canvas"])
        lines.append(f"IMAGES: {image_count} images")
        lines.append("")
    
    return "\n".join(lines)

def generate_export_info(manifest_url: str, manifest_id: str, image_count: int) -> str:
    """
    Generate a summary info file about the export operation.
    
    Args:
        manifest_url: URL of the manifest
        manifest_id: ID of the manifest
        image_count: Number of images exported
        
    Returns:
        str: Formatted export info text
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "LUXPORT EXPORT INFORMATION",
        "=" * 80,
        "",
        f"Export Date: {timestamp}",
        f"Manifest URL: {manifest_url}",
        f"Manifest ID: {manifest_id}",
        f"Images Exported: {image_count}",
        "",
        "This export was created using LuxPort, a utility for exporting IIIF manifest data.",
        "For more information, see: https://github.com/project-lux/luxport",
    ]
    
    return "\n".join(lines) 