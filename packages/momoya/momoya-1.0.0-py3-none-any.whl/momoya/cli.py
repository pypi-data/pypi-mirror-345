#!/usr/bin/env python3
"""
Command-line interface for Momoya image/video extractors
"""
import os
import sys
import argparse
import asyncio
from typing import List, Dict, Any, Optional
import pyfiglet
from termcolor import colored

from momoya.extractors.sora_extractor import SoraExtractor
# Import other extractors as they are added


def print_banner():
    """Display a stylish Momoya banner."""
    banner = pyfiglet.figlet_format("Momoya", font="slant")
    colored_banner = colored(banner, "cyan")
    print(colored_banner)
    print(colored("https://github.com/deidax", "yellow"))
    print(colored("=" * 50, "green"))
    print()


async def extract_sora_content(content_id: Optional[str] = None, 
                             query: Optional[str] = None,
                             auth_token: str = None, 
                             download_dir: str = "downloads", 
                             save_metadata: bool = True,
                             search_similar: bool = True,
                             limit: Optional[int] = None) -> int:
    """Extract Sora AI-generated content using the Sora extractor.
    
    Args:
        content_id: The generation ID to extract (optional)
        query: Text query to search for content (optional)
        auth_token: Authentication token for the API
        download_dir: Directory to save downloads
        save_metadata: Whether to save metadata
        search_similar: Whether to include similar content in results
        limit: Maximum number of results to return
    
    Returns:
        Number of downloaded items
    """
    extractor = SoraExtractor(auth_token=auth_token, download_dir=download_dir)
    return await extractor.run(
        content_id=content_id,
        query=query,
        save_metadata=save_metadata,
        search_similar=search_similar,
        limit=limit
    )


async def main_async():
    """Main async entry point for the CLI."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="Momoya - AI-generated content extractor")
    
    # Platform subparsers
    subparsers = parser.add_subparsers(dest="platform", help="AI platform to extract from")
    
    # Sora extractor arguments
    sora_parser = subparsers.add_parser("sora", help="Extract content from Sora AI")
    sora_group = sora_parser.add_mutually_exclusive_group(required=True)
    sora_group.add_argument("--gen-id", help="Generation ID to extract")
    sora_group.add_argument("--query", help="Text query to search for content")
    sora_parser.add_argument("--auth-token", help="Authentication token for Sora API")
    sora_parser.add_argument("--no-metadata", action="store_true", help="Don't save metadata")
    sora_parser.add_argument("--no-similar", action="store_true", help="Don't fetch similar content")
    sora_parser.add_argument("--limit", type=int, help="Maximum number of results to download")
    sora_parser.add_argument("--output-dir", default="downloads", help="Directory to save downloads")
    
    # Add parsers for other platforms here
    
    # Global arguments
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    args = parser.parse_args()
    
    if args.version:
        from momoya import __version__
        print(f"Momoya v{__version__}")
        return
    
    if not args.platform:
        parser.print_help()
        return
    
    if args.platform == "sora":
        # Get auth token from argument, environment variable, or prompt
        auth_token = args.auth_token
        if not auth_token:
            auth_token = os.environ.get("MOMOYA_SORA_AUTH_TOKEN")
        
        if not auth_token:
            print("Please provide an authentication token for Sora API.")
            print("You can provide it using the --auth-token argument or")
            print("by setting the MOMOYA_SORA_AUTH_TOKEN environment variable.")
            return
        
        # Run the extractor
        downloaded = await extract_sora_content(
            content_id=args.gen_id,
            query=args.query,
            auth_token=auth_token,
            download_dir=args.output_dir,
            save_metadata=not args.no_metadata,
            search_similar=not args.no_similar,
            limit=args.limit
        )
        
        print(f"\nTotal downloaded: {downloaded} files")
        print(f"Files saved to: {os.path.abspath(args.output_dir)}")


def main():
    """Synchronous entry point for the CLI that runs the async main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()