"""
Unit tests for database module functionality
"""
from torbot.modules.database import SearchResultsDatabase
import unittest
import tempfile
import json
from pathlib import Path
import sys
import sqlite3

# Add src to path FIRST, BEFORE any torbot imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# NOW import torbot modules after path is set


class TestSearchResultsDatabase(unittest.TestCase):
    """Test cases for SearchResultsDatabase class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()

    def _create_test_db(self):
        """Create a database instance in the temp directory"""
        test_db_path = self.temp_path / "test_torbot_search_results.db"

        # Create instance manually to use temp directory
        db = SearchResultsDatabase.__new__(SearchResultsDatabase)
        db.db_path = test_db_path
        db.conn = None
        db._init_database()
        return db

    def test_database_initialization(self):
        """Test that database initializes correctly"""
        db = self._create_test_db()
        self.assertIsNotNone(db.conn)

        # Check that tables exist
        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='searches'"
        )
        self.assertIsNotNone(cursor.fetchone())

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='links'"
        )
        self.assertIsNotNone(cursor.fetchone())

        db.close()

    def test_save_search_results(self):
        """Test saving search results to database"""
        db = self._create_test_db()

        test_links = [
            {
                "url": "http://example.onion/page1",
                "title": "Example Page 1",
                "status": 200,
                "classification": "marketplace",
                "accuracy": 0.95,
                "emails": ["contact@example.com"],
                "phone_numbers": []
            },
            {
                "url": "http://example.onion/page2",
                "title": "Example Page 2",
                "status": 404,
                "classification": "forum",
                "accuracy": 0.87,
                "emails": [],
                "phone_numbers": ["+1234567890"]
            }
        ]

        search_id = db.save_search_results(
            root_url="http://example.onion",
            depth=2,
            links_data=test_links
        )

        self.assertIsNotNone(search_id)
        self.assertIsInstance(search_id, int)
        self.assertGreater(search_id, 0)

        db.close()

    def test_get_search_history(self):
        """Test retrieving search history"""
        db = self._create_test_db()

        # Save test data
        test_links = [
            {
                "url": "http://test.onion",
                "title": "Test Page",
                "status": 200,
                "classification": "unknown",
                "accuracy": 0.5,
                "emails": [],
                "phone_numbers": []
            }
        ]

        db.save_search_results(
            root_url="http://test.onion",
            depth=1,
            links_data=test_links
        )

        # Retrieve history
        history = db.get_search_history(limit=10)

        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["root_url"], "http://test.onion")
        self.assertEqual(history[0]["depth"], 1)
        self.assertEqual(history[0]["total_links"], 1)

        db.close()

    def test_get_search_by_id(self):
        """Test retrieving specific search by ID"""
        db = self._create_test_db()

        test_links = [
            {
                "url": "http://example.onion",
                "title": "Example",
                "status": 200,
                "classification": "marketplace",
                "accuracy": 0.95,
                "emails": ["test@example.com"],
                "phone_numbers": ["+1111111111"]
            }
        ]

        search_id = db.save_search_results(
            root_url="http://example.onion",
            depth=1,
            links_data=test_links
        )

        # Retrieve the search
        search = db.get_search_by_id(search_id)

        self.assertIsNotNone(search)
        self.assertEqual(search["id"], search_id)
        self.assertEqual(search["root_url"], "http://example.onion")
        self.assertEqual(search["depth"], 1)
        self.assertEqual(search["total_links"], 1)

        # Check that links_data is parsed from JSON
        self.assertIsInstance(search["links_data"], list)
        self.assertEqual(len(search["links_data"]), 1)
        self.assertEqual(search["links_data"][0]["url"], "http://example.onion")
        self.assertEqual(search["links_data"][0]["title"], "Example")

        db.close()

    def test_filter_by_url(self):
        """Test filtering search history by URL"""
        db = self._create_test_db()

        test_links = [
            {
                "url": "http://test.onion",
                "title": "Test",
                "status": 200,
                "classification": "unknown",
                "accuracy": 0.5,
                "emails": [],
                "phone_numbers": []
            }
        ]

        # Save multiple searches with different URLs
        db.save_search_results("http://url1.onion", 1, test_links)
        db.save_search_results("http://url2.onion", 1, test_links)
        db.save_search_results("http://url1.onion", 2, test_links)

        # Filter by URL
        history = db.get_search_history(root_url="http://url1.onion", limit=10)

        self.assertEqual(len(history), 2)
        for record in history:
            self.assertEqual(record["root_url"], "http://url1.onion")

        db.close()

    def test_database_persistence(self):
        """Test that data persists across connections"""
        test_links = [
            {
                "url": "http://persistent.onion",
                "title": "Persistent",
                "status": 200,
                "classification": "unknown",
                "accuracy": 0.5,
                "emails": [],
                "phone_numbers": []
            }
        ]

        # Save data
        db1 = self._create_test_db()
        search_id = db1.save_search_results("http://persistent.onion", 1, test_links)
        db1_path = db1.db_path
        db1.close()

        # Open new connection and verify data exists
        db2 = SearchResultsDatabase.__new__(SearchResultsDatabase)
        db2.db_path = db1_path
        db2.conn = None
        db2._init_database()

        history = db2.get_search_history(limit=10)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], search_id)

        db2.close()

    def test_save_with_empty_links(self):
        """Test saving search with no links found"""
        db = self._create_test_db()

        search_id = db.save_search_results(
            root_url="http://empty.onion",
            depth=1,
            links_data=[]
        )

        self.assertIsNotNone(search_id)

        search = db.get_search_by_id(search_id)
        self.assertEqual(search["total_links"], 0)
        self.assertEqual(len(search["links_data"]), 0)

        db.close()

    def test_link_metadata_integrity(self):
        """Test that link metadata is preserved correctly"""
        db = self._create_test_db()

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

        search = db.get_search_by_id(search_id)
        saved_link = search["links_data"][0]

        self.assertEqual(saved_link["url"], test_link["url"])
        self.assertEqual(saved_link["title"], test_link["title"])
        self.assertEqual(saved_link["status"], test_link["status"])
        self.assertEqual(saved_link["classification"], test_link["classification"])
        self.assertEqual(saved_link["accuracy"], test_link["accuracy"])
        self.assertEqual(saved_link["emails"], test_link["emails"])
        self.assertEqual(saved_link["phone_numbers"], test_link["phone_numbers"])

        db.close()


if __name__ == "__main__":
    unittest.main()
