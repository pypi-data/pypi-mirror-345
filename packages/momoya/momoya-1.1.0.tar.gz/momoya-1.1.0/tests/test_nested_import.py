#!/usr/bin/env python3
"""
Test to verify that the Momoya package works correctly with the current structure.
This checks if the package can be imported with the current directory structure.
"""
import sys
import os

# Add the parent directory to the Python path to handle the nested structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test if all components of the package can be imported using the correct paths."""
    try:
        # Import the base module (accounting for the nested structure)
        from momoya.momoya import __version__
        print(f"✓ Successfully imported momoya package (version: {__version__})")
        
        # Import the core module
        from momoya.momoya.core.base_extractor import BaseExtractor
        print("✓ Successfully imported BaseExtractor")
        
        # Import the extractors module
        from momoya.momoya.extractors.sora_extractor import SoraExtractor
        print("✓ Successfully imported SoraExtractor")
        
        # Create an instance of the extractor (without authentication)
        extractor = SoraExtractor(auth_token="dummy_token_for_testing")
        print("✓ Successfully created SoraExtractor instance")
        
        # Verify CLI module can be imported
        from momoya.momoya import cli
        print("✓ Successfully imported CLI module")
        
        print("\nAll imports successful! The package structure is correct.")
        print("\nNote: The package has a nested 'momoya' directory structure. When publishing,")
        print("you might want to fix this to avoid requiring users to import via 'momoya.momoya'.")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Momoya package imports...")
    result = test_imports()
    exit(0 if result else 1)