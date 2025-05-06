#!/usr/bin/env python3
"""
Simple test to verify that the Momoya package can be imported correctly.
This helps verify the package is installable before deploying.
"""

def test_imports():
    """Test if all components of the package can be imported."""
    try:
        # Import the base module
        import momoya
        print("✓ Successfully imported momoya base package")
        
        # Import the core module
        from momoya.core.base_extractor import BaseExtractor
        print("✓ Successfully imported BaseExtractor")
        
        # Import the extractors module
        from momoya.extractors.sora_extractor import SoraExtractor
        print("✓ Successfully imported SoraExtractor")
        
        # Create an instance of the extractor (without authentication)
        extractor = SoraExtractor(auth_token="dummy_token_for_testing")
        print("✓ Successfully created SoraExtractor instance")
        
        # Verify CLI module can be imported
        import momoya.cli
        print("✓ Successfully imported CLI module")
        
        print("\nAll imports successful! The package structure is correct.")
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