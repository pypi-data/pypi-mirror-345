"""
Base extractor interface for all AI content extractors
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class BaseExtractor(ABC):
    """Base class that all AI content extractors must implement."""
    
    @abstractmethod
    async def fetch_content_data(self, content_id: Optional[str] = None, query: Optional[str] = None, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Fetch data about AI-generated content using different search methods.
        
        Args:
            content_id: The unique identifier for the content (optional)
            query: Text query to search for content (optional)
            **kwargs: Additional parameters specific to the extractor
            
        Returns:
            Data about the requested content or None if not found
            
        Note:
            Either content_id or query should be provided. Implementation details
            may vary depending on the specific AI platform.
        """
        pass
    
    @abstractmethod
    async def download_content(self, url: str, filename: str) -> bool:
        """Download content from a URL.
        
        Args:
            url: The URL of the content to download
            filename: The filename to save the content as
            
        Returns:
            True if the download was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def save_metadata(self, data: Dict[str, Any], filename: str) -> bool:
        """Save metadata to a file.
        
        Args:
            data: The metadata to save
            filename: The filename to save the metadata as
            
        Returns:
            True if the save was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def process_content_batch(self, content_data: List[Dict[str, Any]], **kwargs) -> int:
        """Process and download multiple content items.
        
        Args:
            content_data: List of content data dictionaries
            **kwargs: Additional parameters specific to the extractor
            
        Returns:
            Number of successfully downloaded content items
        """
        pass
    
    @abstractmethod
    async def run(self, content_id: Optional[str] = None, query: Optional[str] = None, **kwargs) -> int:
        """Run the extractor to fetch and download content.
        
        Args:
            content_id: The ID of the content to extract (optional)
            query: Text query to search for content (optional)
            **kwargs: Additional parameters specific to the extractor
            
        Returns:
            Number of downloaded content items
        """
        pass