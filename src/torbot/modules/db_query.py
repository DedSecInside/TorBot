"""
Utility module for querying and displaying saved search results from the database.
"""
import json
import logging
from datetime import datetime
from typing import List, Optional
from tabulate import tabulate

from .database import SearchResultsDatabase


def display_search_history(
    root_url: Optional[str] = None,
    limit: int = 10,
    verbose: bool = False
) -> None:
    """
    Display search history from the database.

    Args:
        root_url: Optional filter by specific root URL
        limit: Maximum number of records to display
        verbose: If True, show detailed information
    """
    db = SearchResultsDatabase()

    try:
        history = db.get_search_history(root_url=root_url, limit=limit)

        if not history:
            print("No search history found.")
            return

        if verbose:
            print("\n" + "=" * 80)
            print("SEARCH HISTORY")
            print("=" * 80 + "\n")

            for record in history:
                print(f"Search ID: {record['id']}")
                print(f"Root URL: {record['root_url']}")
                print(f"Timestamp: {record['search_timestamp']}")
                print(f"Depth: {record['depth']}")
                print(f"Total Links: {record['total_links']}")
                print("-" * 80 + "\n")
        else:
            table_data = [
                [
                    record["id"],
                    record["root_url"],
                    record["search_timestamp"],
                    record["depth"],
                    record["total_links"]
                ]
                for record in history
            ]
            headers = ["ID", "Root URL", "Timestamp", "Depth", "Total Links"]
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        logging.error(f"Error displaying search history: {e}")
        print(f"Error: {e}")
    finally:
        db.close()


def display_search_details(search_id: int, show_all: bool = False) -> None:
    """
    Display detailed information about a specific search.

    Args:
        search_id: The ID of the search to display
        show_all: If True, show all links; otherwise show summary
    """
    db = SearchResultsDatabase()

    try:
        search = db.get_search_by_id(search_id)

        if not search:
            print(f"Search with ID {search_id} not found.")
            return

        print("\n" + "=" * 80)
        print(f"SEARCH DETAILS - ID: {search_id}")
        print("=" * 80 + "\n")

        print(f"Root URL: {search['root_url']}")
        print(f"Timestamp: {search['search_timestamp']}")
        print(f"Depth: {search['depth']}")
        print(f"Total Links Found: {search['total_links']}")
        print("\n" + "-" * 80)

        links = search["links_data"]

        if show_all:
            print(f"\nDETAILED LINKS ({len(links)} total):\n")
            for idx, link in enumerate(links, 1):
                print(f"{idx}. {link['title']}")
                print(f"   URL: {link['url']}")
                print(f"   Status: {link['status']}")
                print(f"   Category: {link['classification']}")
                if link.get("emails"):
                    print(f"   Emails: {', '.join(link['emails'])}")
                if link.get("phone_numbers"):
                    print(f"   Phone Numbers: {', '.join(link['phone_numbers'])}")
                print()
        else:
            # Show summary table
            table_data = [
                [
                    link["title"],
                    link["url"][:50] + "..." if len(link["url"]) > 50 else link["url"],
                    link["status"],
                    link["classification"]
                ]
                for link in links
            ]
            headers = ["Title", "URL", "Status", "Classification"]
            print("\nLINKS SUMMARY:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        logging.error(f"Error displaying search details: {e}")
        print(f"Error: {e}")
    finally:
        db.close()


def export_search_to_json(search_id: int, output_file: str) -> None:
    """
    Export a specific search to a JSON file.

    Args:
        search_id: The ID of the search to export
        output_file: The output file path
    """
    db = SearchResultsDatabase()

    try:
        search = db.get_search_by_id(search_id)

        if not search:
            print(f"Search with ID {search_id} not found.")
            return

        export_data = {
            "search_id": search["id"],
            "root_url": search["root_url"],
            "search_timestamp": search["search_timestamp"],
            "depth": search["depth"],
            "total_links": search["total_links"],
            "links": search["links_data"]
        }

        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Search {search_id} exported to {output_file}")

    except Exception as e:
        logging.error(f"Error exporting search: {e}")
        print(f"Error: {e}")
    finally:
        db.close()


def get_statistics() -> None:
    """Display general statistics about all saved searches."""
    db = SearchResultsDatabase()

    try:
        history = db.get_search_history(limit=None)

        if not history:
            print("No searches found in database.")
            return

        total_searches = len(history)
        total_links = sum(record["total_links"] for record in history)
        avg_links = total_links / total_searches if total_searches > 0 else 0
        avg_depth = sum(record["depth"] for record in history) / total_searches if total_searches > 0 else 0

        unique_urls = len(set(record["root_url"] for record in history))

        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80 + "\n")
        print(f"Total Searches: {total_searches}")
        print(f"Unique Root URLs: {unique_urls}")
        print(f"Total Links Found: {total_links}")
        print(f"Average Links per Search: {avg_links:.2f}")
        print(f"Average Crawl Depth: {avg_depth:.2f}")
        print()

    except Exception as e:
        logging.error(f"Error getting statistics: {e}")
        print(f"Error: {e}")
    finally:
        db.close()
