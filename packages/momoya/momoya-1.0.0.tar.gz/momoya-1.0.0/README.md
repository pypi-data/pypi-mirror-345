# Momoya

A Python package for extracting AI-generated images and videos from various platforms.

## Features

- Extract AI-generated images and videos with associated metadata
- Command-line interface for easy usage
- Multiple search methods: by content ID or by text query

## Currently Supported Platforms

- **Sora AI**: Extracts images/videos and metadata using gen_id or text query

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/momoya.git
cd momoya

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

The package provides a command-line interface for easy usage:

```bash
# Set your authentication token (recommended)
export MOMOYA_SORA_AUTH_TOKEN="your_auth_token_here"

# Extract content from Sora using generation ID
python -m momoya.cli sora --gen-id gen_01jt5veqacf4tsvcwa76kb908m

# Search for content using a text query
python -m momoya.cli sora --query "selfie with a dog"

# Save to a specific directory
python -m momoya.cli sora --query "space exploration" --output-dir my_downloads

# Limit the number of results
python -m momoya.cli sora --query "sunset beach" --limit 10

# Skip saving metadata
python -m momoya.cli sora --gen-id gen_01jt5veqacf4tsvcwa76kb908m --no-metadata
```

### Python API

You can also use the package in your Python code:

```python
import asyncio
from momoya.extractors.sora_extractor import SoraExtractor

async def download_sora_content():
    # Initialize the extractor
    extractor = SoraExtractor(
        auth_token="your_auth_token_here",
        download_dir="downloads"
    )
    
    # Example 1: Download content by generation ID
    gen_id = "gen_01jt5veqacf4tsvcwa76kb908m"
    downloaded = await extractor.run(content_id=gen_id, save_metadata=True)
    print(f"Downloaded {downloaded} items using generation ID")
    
    # Example 2: Search and download content by text query
    query = "abstract art in vibrant colors"
    downloaded = await extractor.run(
        query=query, 
        save_metadata=True,
        limit=5,  # Limit to 5 results
    )
    print(f"Downloaded {downloaded} items using text query")

# Run the async function
asyncio.run(download_sora_content())
```

## Adding New Extractors

The package is designed to be easily extensible with new extractors for different AI platforms:

1. Create a new extractor class in the `momoya/extractors` directory
2. Implement the `BaseExtractor` interface
3. Add the new extractor to the CLI in `momoya/cli.py`

## Authentication

Most AI platforms require authentication to access their platforms (Bearer token)

## License

MIT