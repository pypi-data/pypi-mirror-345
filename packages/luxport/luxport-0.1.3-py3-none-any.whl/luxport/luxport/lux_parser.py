"""
Module for parsing and processing Lux API URLs and retrieving data in either Lux or Linked Art format.
"""

import json
import re
import requests
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urlparse


class LuxParser:
    """Class to handle parsing Lux URLs and retrieving IIIF manifests."""

    def __init__(self):
        self.lux_pattern = r"https?://lux\.collections\.yale\.edu/data/object/([a-zA-Z0-9-]+)"
        self.linked_art_pattern = r"https?://linked-art\.library\.yale\.edu/node/([a-zA-Z0-9-]+)"

    def is_lux_url(self, url: str) -> bool:
        """Check if the URL is a Lux URL."""
        return bool(re.match(self.lux_pattern, url))

    def is_linked_art_url(self, url: str) -> bool:
        """Check if the URL is a Linked Art URL."""
        return bool(re.match(self.linked_art_pattern, url))

    def get_object_id(self, url: str) -> Optional[str]:
        """Extract the object ID from a Lux or Linked Art URL."""
        lux_match = re.match(self.lux_pattern, url)
        if lux_match:
            return lux_match.group(1)
        
        linked_art_match = re.match(self.linked_art_pattern, url)
        if linked_art_match:
            return linked_art_match.group(1)
        
        return None

    def fetch_lux_data(self, object_id: str) -> Dict[str, Any]:
        """Fetch data from the Lux API."""
        url = f"https://lux.collections.yale.edu/data/object/{object_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def fetch_linked_art_data(self, object_id: str) -> Dict[str, Any]:
        """Fetch data from the Linked Art API."""
        url = f"https://linked-art.library.yale.edu/node/{object_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_data(self, url: str, format: str = "lux") -> Dict[str, Any]:
        """
        Get data for an object from either format.
        
        Args:
            url: The Lux or Linked Art URL
            format: Either 'lux' or 'la' (for Linked Art)
            
        Returns:
            The JSON data from the API
        """
        object_id = self.get_object_id(url)
        if not object_id:
            raise ValueError(f"Invalid Lux or Linked Art URL: {url}")
        
        # If it's a Linked Art URL, extract the ID and get Lux data if needed
        if self.is_linked_art_url(url):
            if format.lower() == "la":
                return self.fetch_linked_art_data(object_id)
            else:
                # Find equivalent Lux ID from Linked Art data
                la_data = self.fetch_linked_art_data(object_id)
                # Look for equivalent Lux ID in the Linked Art data
                for equiv in la_data.get("equivalent", []):
                    if "lux.collections.yale.edu" in equiv.get("id", ""):
                        lux_id = self.get_object_id(equiv["id"])
                        if lux_id:
                            return self.fetch_lux_data(lux_id)
                
                # If no equivalent found, raise error
                raise ValueError(f"Could not find equivalent Lux data for Linked Art ID: {object_id}")
        
        # It's a Lux URL
        if format.lower() == "la":
            # Find equivalent Linked Art ID from Lux data
            lux_data = self.fetch_lux_data(object_id)
            for equiv in lux_data.get("equivalent", []):
                if "linked-art.library.yale.edu" in equiv.get("id", ""):
                    la_id = self.get_object_id(equiv["id"])
                    if la_id:
                        return self.fetch_linked_art_data(la_id)
            
            # If no equivalent found, raise error
            raise ValueError(f"Could not find equivalent Linked Art data for Lux ID: {object_id}")
        else:
            return self.fetch_lux_data(object_id)
    
    def find_iiif_manifests(self, data: Dict[str, Any]) -> List[str]:
        """Extract IIIF manifest URLs from Lux or Linked Art data."""
        manifest_urls = []
        
        # Check if we got Lux data
        if "subject_of" in data:
            # Process Lux data
            for subject in data.get("subject_of", []):
                if subject.get("_label") == "Content of IIIF Manifest":
                    for carrier in subject.get("digitally_carried_by", []):
                        for access_point in carrier.get("access_point", []):
                            if "collections.library.yale.edu/manifests" in access_point.get("id", ""):
                                manifest_urls.append(access_point["id"])
        
        # Check if we got Linked Art data (different structure)
        elif "subject_of" in data:
            # Process Linked Art data structure - similar to Lux data
            for subject in data.get("subject_of", []):
                if subject.get("_label") == "Content of IIIF Manifest":
                    for carrier in subject.get("digitally_carried_by", []):
                        for access_point in carrier.get("access_point", []):
                            if "collections.library.yale.edu/manifests" in access_point.get("id", ""):
                                manifest_urls.append(access_point["id"])
        
        return manifest_urls


def process_lux_url(url: str, format: str = "lux") -> List[str]:
    """
    Process a Lux or Linked Art URL and return a list of IIIF manifest URLs.
    
    Args:
        url: A Lux or Linked Art URL
        format: 'lux' or 'la' for the API format to use
        
    Returns:
        A list of IIIF manifest URLs
    """
    parser = LuxParser()
    data = parser.get_data(url, format)
    return parser.find_iiif_manifests(data) 