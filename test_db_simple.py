#!/usr/bin/env python3
"""
Simple test script to verify database functionality without pytest
"""
from torbot.modules.database import SearchResultsDatabase
import sys
import tempfile
from pathlib import Path

# Add src to path BEFORE importing torbot
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_save_and_retrieve():
    """Test basic save and retrieve operations"""
    print("Testing basic save and retrieve...")

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

            assert search_id is not None, "Search ID should not be None"
            print(f"✓ Successfully saved search with ID: {search_id}")

            # Test retrieve
            history = db.get_search_history(limit=10)
            assert len(history) > 0, "Should have at least one search in history"
            assert history[0]["root_url"] == "http://test.onion", "URL should match"
            print(f"✓ Successfully retrieved search history: {len(history)} records")

            # Test get by ID
            search = db.get_search_by_id(search_id)
            assert search is not None, "Search should be found"
            assert search["total_links"] == 1, "Should have 1 link"
            assert len(search["links_data"]) == 1, "Should have 1 link data"
            print(f"✓ Successfully retrieved search by ID with {search['total_links']} links")

            db.close()

        finally:
            # Restore original
            db_module.project_root_directory = original_root


def test_multiple_searches():
    """Test saving multiple searches"""
    print("\nTesting multiple searches...")

    with tempfile.TemporaryDirectory() as temp_dir:
        import torbot.modules.database as db_module
        original_root = db_module.project_root_directory
        db_module.project_root_directory = temp_dir

        try:
            db = SearchResultsDatabase()

            # Save multiple searches
            for i in range(3):
                test_links = [
                    {
                        "url": f"http://test{i}.onion",
                        "title": f"Test Page {i}",
                        "status": 200,
                        "classification": "forum",
                        "accuracy": 0.8 + (i * 0.05),
                        "emails": [],
                        "phone_numbers": []
                    }
                ]

                search_id = db.save_search_results(
                    root_url=f"http://test{i}.onion",
                    depth=1,
                    links_data=test_links
                )
                print(f"  Saved search {i+1} with ID: {search_id}")

            # Verify all were saved
            history = db.get_search_history(limit=10)
            assert len(history) == 3, f"Should have 3 searches, got {len(history)}"
            print(f"✓ Successfully saved and retrieved {len(history)} searches")

            db.close()

        finally:
            db_module.project_root_directory = original_root


def test_filter_by_url():
    """Test filtering search history by URL"""
    print("\nTesting filter by URL...")

    with tempfile.TemporaryDirectory() as temp_dir:
        import torbot.modules.database as db_module
        original_root = db_module.project_root_directory
        db_module.project_root_directory = temp_dir

        try:
            db = SearchResultsDatabase()

            # Save searches with different URLs
            test_links = [{"url": "http://test", "title": "Test", "status": 200,
                          "classification": "unknown", "accuracy": 0.5,
                           "emails": [], "phone_numbers": []}]

            db.save_search_results("http://url1.onion", 1, test_links)
            db.save_search_results("http://url2.onion", 1, test_links)
            db.save_search_results("http://url1.onion", 2, test_links)

            # Filter by URL
            history = db.get_search_history(root_url="http://url1.onion", limit=10)
            assert len(history) == 2, f"Should have 2 searches for url1, got {len(history)}"
            for record in history:
                assert record["root_url"] == "http://url1.onion", "URL should match filter"
            print(f"✓ Successfully filtered results: found {len(history)} searches for http://url1.onion")

            db.close()

        finally:
            db_module.project_root_directory = original_root


def test_metadata_preservation():
    """Test that metadata is correctly preserved"""
    print("\nTesting metadata preservation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        import torbot.modules.database as db_module
        original_root = db_module.project_root_directory
        db_module.project_root_directory = temp_dir

        try:
            db = SearchResultsDatabase()

            # Save complex metadata
            test_link = {
                "url": "http://metadata.test/page",
                "title": "Test Page Title",
                "status": 403,
                "classification": "forum",
                "accuracy": 0.89,
                "emails": ["admin@test.com", "support@test.com"],
                "phone_numbers": ["+1234567890", "+0987654321"]
            }

            search_id = db.save_search_results(
                root_url="http://metadata.test",
                depth=1,
                links_data=[test_link]
            )

            # Retrieve and verify
            search = db.get_search_by_id(search_id)
            saved_link = search["links_data"][0]

            assert saved_link["url"] == test_link["url"], "URL mismatch"
            assert saved_link["title"] == test_link["title"], "Title mismatch"
            assert saved_link["status"] == test_link["status"], "Status mismatch"
            assert saved_link["classification"] == test_link["classification"], "Classification mismatch"
            assert saved_link["accuracy"] == test_link["accuracy"], "Accuracy mismatch"
            assert saved_link["emails"] == test_link["emails"], "Emails mismatch"
            assert saved_link["phone_numbers"] == test_link["phone_numbers"], "Phone numbers mismatch"

            print(f"✓ Metadata correctly preserved")
            print(f"  - URL: {saved_link['url']}")
            print(f"  - Title: {saved_link['title']}")
            print(f"  - Status: {saved_link['status']}")
            print(f"  - Classification: {saved_link['classification']}")
            print(f"  - Emails: {saved_link['emails']}")
            print(f"  - Phone numbers: {saved_link['phone_numbers']}")

            db.close()

        finally:
            db_module.project_root_directory = original_root


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Database Module")
    print("=" * 60)

    try:
        test_basic_save_and_retrieve()
        test_multiple_searches()
        test_filter_by_url()
        test_metadata_preservation()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
