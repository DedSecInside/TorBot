"""
Module for handling database operations for storing search results.
Uses SQLite for lightweight database management.
"""
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .config import project_root_directory


class SearchResultsDatabase:
    """
    Manages SQLite database for storing TorBot search results.
    Each record contains:
    - root_url: The root URL that was crawled
    - search_timestamp: When the search was performed
    - depth: Crawl depth
    - links: JSON array of discovered links with their metadata
    - total_links: Count of total links found
    """

    DB_NAME = "torbot_search_results.db"

    def __init__(self):
        """Initialize database connection."""
        self.db_path = Path(project_root_directory) / self.DB_NAME
        self.conn = None
        self._init_database()

    def _init_database(self) -> None:
        """Create database and tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            # Create searches table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    root_url TEXT NOT NULL,
                    search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    depth INTEGER NOT NULL,
                    total_links INTEGER NOT NULL,
                    links_data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create links table for easier querying
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    status_code INTEGER,
                    classification TEXT,
                    accuracy REAL,
                    emails TEXT,
                    phone_numbers TEXT,
                    FOREIGN KEY (search_id) REFERENCES searches(id) ON DELETE CASCADE
                )
                """
            )

            self.conn.commit()
            logging.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def save_search_results(
        self,
        root_url: str,
        depth: int,
        links_data: List[Dict[str, Any]]
    ) -> int:
        """
        Save search results to the database.

        Args:
            root_url: The root URL that was crawled
            depth: Crawl depth
            links_data: List of link dictionaries containing:
                - url: Link URL
                - title: Page title
                - status: HTTP status code
                - classification: Content classification
                - accuracy: Classification accuracy
                - emails: List of emails found
                - phone_numbers: List of phone numbers found

        Returns:
            search_id: The ID of the inserted search record
        """
        if not self.conn:
            self._init_database()

        try:
            cursor = self.conn.cursor()
            search_timestamp = datetime.now().isoformat()

            # Insert into searches table
            cursor.execute(
                """
                INSERT INTO searches (root_url, search_timestamp, depth, total_links, links_data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    root_url,
                    search_timestamp,
                    depth,
                    len(links_data),
                    json.dumps(links_data, indent=2)
                )
            )

            search_id = cursor.lastrowid

            # Insert individual links for better querying
            for link in links_data:
                cursor.execute(
                    """
                    INSERT INTO links (search_id, url, title, status_code, classification, accuracy, emails, phone_numbers)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        search_id,
                        link.get("url"),
                        link.get("title"),
                        link.get("status"),
                        link.get("classification"),
                        link.get("accuracy"),
                        json.dumps(link.get("emails", [])),
                        json.dumps(link.get("phone_numbers", []))
                    )
                )

            self.conn.commit()
            logging.info(f"Saved {len(links_data)} links to database for {root_url}")
            return search_id

        except sqlite3.Error as e:
            logging.error(f"Error saving search results: {e}")
            raise

    def get_search_history(self, root_url: str = None, limit: int = 10) -> List[Dict]:
        """
        Retrieve search history from the database.

        Args:
            root_url: Optional filter by root URL
            limit: Maximum number of records to retrieve

        Returns:
            List of search records
        """
        if not self.conn:
            self._init_database()

        try:
            cursor = self.conn.cursor()

            if root_url:
                cursor.execute(
                    """
                    SELECT id, root_url, search_timestamp, depth, total_links
                    FROM searches
                    WHERE root_url = ?
                    ORDER BY search_timestamp DESC
                    LIMIT ?
                    """,
                    (root_url, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, root_url, search_timestamp, depth, total_links
                    FROM searches
                    ORDER BY search_timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logging.error(f"Error retrieving search history: {e}")
            return []

    def get_search_by_id(self, search_id: int) -> Dict:
        """
        Retrieve detailed search results by ID.

        Args:
            search_id: The search record ID

        Returns:
            Dictionary containing search details and links
        """
        if not self.conn:
            self._init_database()

        try:
            cursor = self.conn.cursor()

            # Get search metadata
            cursor.execute(
                """
                SELECT * FROM searches WHERE id = ?
                """,
                (search_id,)
            )
            search = cursor.fetchone()

            if not search:
                return None

            search_dict = dict(search)
            search_dict["links_data"] = json.loads(search_dict["links_data"])

            return search_dict

        except sqlite3.Error as e:
            logging.error(f"Error retrieving search by ID: {e}")
            return None

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logging.debug("Database connection closed")
