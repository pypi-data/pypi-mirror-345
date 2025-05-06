"""
Sora AI content extractor implementation
"""
import os
import json
import asyncio
import random
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from urllib.parse import urlparse

import aiohttp
import aiofiles

from momoya.core.base_extractor import BaseExtractor


# List of common user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/112.0.0.0",
]


class SoraExtractor(BaseExtractor):
    """Extractor for Sora AI-generated content (images and videos)."""
    
    def __init__(self, auth_token: str = "YOUR_AUTH_TOKEN_HERE", download_dir: str = "downloads",
                max_retries: int = 3, retry_delay: float = 2.0, rotate_user_agent_after: int = 5):
        """Initialize the Sora Content Extractor.
        
        Args:
            auth_token: Your authentication token for the Sora API.
            download_dir: Directory where downloads will be saved.
            max_retries: Maximum number of download retry attempts.
            retry_delay: Delay in seconds between retry attempts.
            rotate_user_agent_after: Number of requests after which to rotate the user-agent.
        """
        self.auth_token = auth_token
        self.download_dir = download_dir
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rotate_user_agent_after = rotate_user_agent_after
        self.request_count = 0
        
        # Select initial random user agent
        self.current_user_agent = random.choice(USER_AGENTS)
        
        self.headers = {
            "authority": "sora.chatgpt.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://sora.chatgpt.com",
            "referer": "https://sora.chatgpt.com/explore",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.current_user_agent
        }
        
        if self.auth_token == "YOUR_AUTH_TOKEN_HERE":
            print("WARNING: You're using the default auth token placeholder.")
            print("Please update the auth_token with your own authentication token.")
        
        self.headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Ensure main download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Create subdirectories for images and videos
        self.images_dir = os.path.join(self.download_dir, "images")
        self.videos_dir = os.path.join(self.download_dir, "videos")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def _maybe_rotate_user_agent(self):
        """Rotate the user agent after a certain number of requests."""
        self.request_count += 1
        if self.request_count >= self.rotate_user_agent_after:
            self.current_user_agent = random.choice(USER_AGENTS)
            self.headers["user-agent"] = self.current_user_agent
            self.request_count = 0
            print(f"Rotated user agent to: {self.current_user_agent}")
    
    def _detect_content_type(self, url: str) -> Tuple[str, str]:
        """Detect if the content is an image or video based on the URL.
        
        Args:
            url: The URL of the content
            
        Returns:
            A tuple of (content_type, file_extension)
            content_type is either 'image' or 'video'
        """
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Extract file extension from URL
        # Use regex to find the extension in the URL path
        ext_match = re.search(r'\.([a-zA-Z0-9]+)(?:\?|$)', path)
        if ext_match:
            ext = ext_match.group(1).lower()
        else:
            # Default to png if no extension found
            ext = "png"
        
        # Determine content type based on extension
        video_extensions = ['mp4', 'mov', 'avi', 'wmv', 'webm', 'mkv', 'flv']
        if ext in video_extensions:
            return 'video', ext
        else:
            # Default to image for all other extensions
            return 'image', ext
    
    def _get_appropriate_directory(self, content_type: str) -> str:
        """Get the appropriate directory for the content type.
        
        Args:
            content_type: Either 'image' or 'video'
            
        Returns:
            Path to the appropriate directory
        """
        if content_type == 'video':
            return self.videos_dir
        else:
            return self.images_dir
    
    async def fetch_content_data(self, content_id: Optional[str] = None, query: Optional[str] = None, search_similar: bool = True, limit: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Fetch data about AI-generated content using different search methods.
        
        Args:
            content_id: The generation ID (gen_id) to search for similar content (optional)
            query: Text query to search for content (optional)
            search_similar: If True, return similar content in addition to the exact match
            limit: Maximum number of similar content to return, None means all available
            
        Returns:
            Data about the requested content(s) or None if not found
            
        Note:
            Either content_id or query must be provided. If both are provided,
            content_id takes precedence.
        """
        url = "https://sora.chatgpt.com/backend/search"
        
        # Create payload based on search type
        if content_id:
            # Search by similar content (content_id)
            payload = {
                "similar_to": [content_id],
                "query": ""
            }
        elif query:
            # Search by text query
            payload = {
                "query": query
            }
        else:
            print("Error: Either content_id or query must be provided")
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if "data" in data and len(data["data"]) > 0:
                        if search_similar:
                            # Return all content without limit
                            results = []
                            for item in data["data"]:
                                gen = item.get("generation", {})
                                results.append(gen)
                                
                            # Check if there's more data to fetch using pagination
                            has_more = data.get("has_more", False)
                            last_id = data.get("last_id", None)
                            
                            # Continue fetching if there are more results
                            while has_more and last_id:
                                print(f"Fetching more content... (last_id: {last_id})")
                                
                                # Update payload for pagination
                                pagination_payload = payload.copy()
                                pagination_payload["after"] = last_id
                                
                                async with session.post(url, headers=self.headers, json=pagination_payload) as paginated_response:
                                    paginated_response.raise_for_status()
                                    paginated_data = await paginated_response.json()
                                    
                                    if "data" in paginated_data and len(paginated_data["data"]) > 0:
                                        for item in paginated_data["data"]:
                                            gen = item.get("generation", {})
                                            results.append(gen)
                                        
                                        has_more = paginated_data.get("has_more", False)
                                        last_id = paginated_data.get("last_id", None)
                                    else:
                                        break
                            
                            # Apply limit if provided
                            if limit is not None and len(results) > limit:
                                results = results[:limit]
                                
                            print(f"Total content found: {len(results)}")
                            return results
                        else:
                            # Return only the exact match or the first result
                            if content_id:
                                for item in data["data"]:
                                    gen = item.get("generation", {})
                                    if gen.get("id") == content_id:
                                        return gen
                            
                            # If we didn't find an exact match, return the first result
                            return data["data"][0].get("generation", {})
                    else:
                        search_type = f"gen_id: {content_id}" if content_id else f"query: {query}"
                        print(f"No data found for {search_type}")
                        return None
        
        except aiohttp.ClientError as e:
            print(f"Error making request: {e}")
            return None
        except json.JSONDecodeError:
            print("Error parsing response as JSON")
            return None
    
    async def download_content(self, url: str, filename: str) -> bool:
        """Download content (image or video) from a URL asynchronously with retry logic.
        
        Args:
            url: The URL of the content to download
            filename: The filename to save the content as
            
        Returns:
            True if the download was successful, False otherwise
        """
        # Detect content type and get appropriate directory
        content_type, file_extension = self._detect_content_type(url)
        target_dir = self._get_appropriate_directory(content_type)
        
        # Update filename with proper extension if needed
        base_filename = os.path.splitext(filename)[0]  # Remove any existing extension
        filename_with_ext = f"{base_filename}.{file_extension}"
        
        filepath = os.path.join(target_dir, filename_with_ext)
        
        # Check if the file already exists
        if os.path.exists(filepath):
            print(f"File already exists, skipping: {filename_with_ext} ({content_type})")
            return True
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Rotate user agent if needed
                self._maybe_rotate_user_agent()
                
                # Use a more browser-like set of headers for downloading content
                # Do not include the Authorization header which is causing the 403 error
                download_headers = {
                    "User-Agent": self.current_user_agent,
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,video/*,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://sora.chatgpt.com/",
                    "Sec-Fetch-Dest": "image",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Site": "cross-site",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache"
                }
                
                connector = aiohttp.TCPConnector(ssl=False, force_close=True)
                timeout = aiohttp.ClientTimeout(total=60)  # 60-second timeout
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=download_headers) as session:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        
                        # Create a temporary file first
                        temp_filepath = f"{filepath}.tmp"
                        async with aiofiles.open(temp_filepath, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                await f.write(chunk)
                        
                        # Rename the temporary file to the actual filename
                        os.rename(temp_filepath, filepath)
                
                print(f"Downloaded: {filename_with_ext} ({content_type})")
                return True
            
            except aiohttp.ClientResponseError as e:
                print(f"Error downloading {filename_with_ext} (attempt {attempt}/{self.max_retries}): {e.status}, message='{e.message}'")
                
                # Try with a signed URL if we're getting authentication errors
                if e.status == 403:
                    if attempt == self.max_retries:
                        print("Authentication failed. The URL might be expired or require special access.")
            except aiohttp.ClientConnectorError as e:
                print(f"Connection error while downloading {filename_with_ext} (attempt {attempt}/{self.max_retries}): {e}")
            except aiohttp.ClientPayloadError as e:
                print(f"Payload error while downloading {filename_with_ext} (attempt {attempt}/{self.max_retries}): {e}")
            except aiohttp.ServerDisconnectedError as e:
                print(f"Server disconnected while downloading {filename_with_ext} (attempt {attempt}/{self.max_retries}): {e}")
            except asyncio.TimeoutError:
                print(f"Timeout while downloading {filename_with_ext} (attempt {attempt}/{self.max_retries})")
            except Exception as e:
                print(f"Error downloading {filename_with_ext} (attempt {attempt}/{self.max_retries}): {e}")
            
            # If we're not on the last attempt, wait before retrying
            if attempt < self.max_retries:
                # Add jitter to the retry delay (between 0.5x and 1.5x the base delay)
                jittered_delay = self.retry_delay * (0.5 + random.random())
                print(f"Retrying in {jittered_delay:.2f} seconds...")
                await asyncio.sleep(jittered_delay)
            else:
                print(f"Failed to download {filename_with_ext} after {self.max_retries} attempts")
        
        return False
    
    async def save_metadata(self, data: Dict[str, Any], filename: str) -> bool:
        """Save metadata to a JSON file asynchronously.
        
        Args:
            data: The metadata to save
            filename: The filename to save the metadata as
            
        Returns:
            True if the save was successful, False otherwise
        """
        try:
            # Save metadata to the main download directory
            filepath = os.path.join(self.download_dir, filename)
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
            print(f"Saved metadata: {filename}")
            return True
        
        except Exception as e:
            print(f"Error saving metadata {filename}: {e}")
            return False
    
    async def process_content_batch(self, content_data: List[Dict[str, Any]], save_metadata: bool = True, batch_size: int = 5) -> int:
        """Process and download multiple content items with controlled concurrency.
        
        Args:
            content_data: List of content data dictionaries
            save_metadata: Whether to save metadata for each content item
            batch_size: Number of concurrent downloads
            
        Returns:
            Number of successfully downloaded content items
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        successful_downloads = 0
        total_items = len(content_data)
        
        # Process in batches to limit concurrency
        for i in range(0, total_items, batch_size):
            batch = content_data[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(total_items + batch_size - 1)//batch_size} " +
                  f"({len(batch)} items, {i+1}-{min(i+len(batch), total_items)}/{total_items})")
            
            download_tasks = []
            metadata_tasks = []
            
            for item in batch:
                if item and 'url' in item and item['url']:
                    item_id = item.get('id', 'unknown')
                    # Create base filename without extension (extension will be added in download_content)
                    base_filename = f"{item_id}_{timestamp}"
                    download_tasks.append(self.download_content(item['url'], base_filename))
                    
                    # Create metadata task if requested
                    if save_metadata:
                        meta_filename = f"{item_id}_{timestamp}.json"
                        metadata_tasks.append(self.save_metadata(item, meta_filename))
            
            # Execute all download tasks in the current batch
            download_results = await asyncio.gather(*download_tasks, return_exceptions=False)
            
            # Execute all metadata tasks if any
            if metadata_tasks:
                await asyncio.gather(*metadata_tasks, return_exceptions=False)
            
            # Count successful downloads in this batch
            batch_successful = sum(1 for result in download_results if result is True)
            successful_downloads += batch_successful
            
            if batch_successful < len(download_tasks):
                print(f"Warning: {len(download_tasks) - batch_successful} downloads failed in the current batch")
            
            # Add a small delay between batches to avoid overwhelming the server
            if i + batch_size < total_items:
                delay = random.uniform(1.0, 3.0)
                print(f"Pausing for {delay:.2f} seconds before next batch...")
                await asyncio.sleep(delay)
        
        return successful_downloads
    
    async def run(self, content_id: Optional[str] = None, query: Optional[str] = None, save_metadata: bool = True, search_similar: bool = True, limit: Optional[int] = None) -> int:
        """Run the extractor to fetch and download content.
        
        Args:
            content_id: The generation ID to search for (optional)
            query: Text query to search for content (optional)
            save_metadata: Whether to save metadata for each content item
            search_similar: If True, return similar content in addition to the exact match
            limit: Maximum number of similar content to return, None means all available
            
        Returns:
            Number of downloaded content items
            
        Note:
            Either content_id or query must be provided. If both are provided,
            content_id takes precedence.
        """
        if content_id:
            print(f"Fetching data for gen_id: {content_id}")
        elif query:
            print(f"Searching for content with query: {query}")
        else:
            print("Error: Either content_id or query must be provided")
            return 0
            
        content_data = await self.fetch_content_data(content_id=content_id, query=query, 
                                                  search_similar=search_similar, limit=limit)
        
        if not content_data:
            search_type = f"gen_id: {content_id}" if content_id else f"query: {query}"
            print(f"No data found for {search_type}")
            return 0
        
        # Handle both single content result and list of content
        if isinstance(content_data, dict):
            content_data = [content_data]
            
        print(f"Found {len(content_data)} content items. Downloading...")
        downloaded = await self.process_content_batch(content_data, save_metadata)
        
        print(f"Download complete. Successfully downloaded {downloaded} content items.")
        return downloaded