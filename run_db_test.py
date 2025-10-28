#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to path first
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Now import and run the test
if __name__ == "__main__":
    from torbot.modules.database import SearchResultsDatabase
    import tempfile

    print("=" * 60)
    print("Testing Database Module")
    print("=" * 60)

    print("\nTesting basic save and retrieve...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch the project root
        import torbot.modules.database as db_module
        original_root = db_module.project_root_directory
        db_module.project_root_directory = temp_dir

        try:
            db = SearchResultsDatabase()

            # Test save
            test_links = [
                {
                    "url": "http://test.onion/page1",
                    "title": "Test Page",
                    "status": 200,
                    "classification": "marketplace",
                    "accuracy": 0.95,
                    "emails": ["test@example.com"],
                    "phone_numbers": []
                }
            ]

            search_id = db.save_search_results(
                root_url="http://test.onion",
                depth=1,
                links_data=test_links
            )

            print(f"✓ Successfully saved search with ID: {search_id}")

            # Test retrieve
            history = db.get_search_history(limit=10)
            print(f"✓ Successfully retrieved {len(history)} searches")

            # Test get by ID
            search = db.get_search_by_id(search_id)
            print(f"✓ Retrieved search by ID with {search['total_links']} links")

            db.close()
            print("\n✓ ALL TESTS PASSED")

        finally:
            db_module.project_root_directory = original_root
