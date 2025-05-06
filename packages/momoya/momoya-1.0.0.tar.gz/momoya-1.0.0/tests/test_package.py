#!/usr/bin/env python3
"""
Basic test script to verify the Momoya package is correctly installed
"""
import sys

def test_package():
    """
    Test if the Momoya package can be imported and used correctly.
    This test doesn't require an actual API token.
    """
    try:
        # Import the package
        import momoya
        print(f"✓ Successfully imported momoya package")
        
        # Try to import the SoraExtractor class
        try:
            from momoya.extractors.sora_extractor import SoraExtractor
            print(f"✓ Successfully imported SoraExtractor")
        except ImportError:
            # If the direct import fails, try with the nested structure
            try:
                from momoya.momoya.extractors.sora_extractor import SoraExtractor
                print(f"✓ Successfully imported SoraExtractor (from nested path)")
            except ImportError:
                print("❌ Failed to import SoraExtractor (tried both direct and nested paths)")
                return False
        
        # Create an instance of SoraExtractor
        extractor = SoraExtractor(auth_token="test_token", download_dir="test_downloads")
        print(f"✓ Successfully created SoraExtractor instance")
        
        # Print all available attributes and methods
        print("\nVerifying SoraExtractor attributes and methods:")
        methods = [attr for attr in dir(extractor) if not attr.startswith('_')]
        for method in methods:
            print(f"  - {method}")
        
        print("\nPackage check complete - Momoya is correctly installed and ready to use!")
        return True
    except Exception as e:
        print(f"❌ Error during package test: {e}")
        return False

if __name__ == "__main__":
    print("Testing if the Momoya package is correctly installed and functional...\n")
    success = test_package()
    sys.exit(0 if success else 1)