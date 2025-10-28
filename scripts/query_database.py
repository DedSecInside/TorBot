#!/usr/bin/env python3
"""
Command-line tool for querying TorBot search results from the database.
Usage: python query_database.py [options]
"""
from torbot.modules.db_query import (
    display_search_history,
    display_search_details,
    export_search_to_json,
    get_statistics
)
import sys
import argparse
import logging
from pathlib import Path

# Add the src directory to the path to import torbot modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S"
    )


def main() -> None:
    """Main entry point for the database query tool."""
    parser = argparse.ArgumentParser(
        prog="TorBot DB Query",
        description="Query and display TorBot search results from the database."
    )

    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # History command
    history_parser = subparsers.add_parser(
        "history",
        help="Display search history"
    )
    history_parser.add_argument(
        "-u", "--url",
        type=str,
        help="Filter by root URL"
    )
    history_parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Maximum number of records to display (default: 10)"
    )
    history_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed information"
    )

    # Details command
    details_parser = subparsers.add_parser(
        "details",
        help="Display detailed information about a specific search"
    )
    details_parser.add_argument(
        "search_id",
        type=int,
        help="Search ID to display"
    )
    details_parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Show all links in detailed format"
    )

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export search results to JSON file"
    )
    export_parser.add_argument(
        "search_id",
        type=int,
        help="Search ID to export"
    )
    export_parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output file path (JSON format)"
    )

    # Statistics command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Display database statistics"
    )

    args = parser.parse_args()

    # Setup logging
    verbose = getattr(args, "verbose", False)
    setup_logging(verbose)

    # Handle commands
    if args.command == "history":
        display_search_history(
            root_url=args.url,
            limit=args.limit,
            verbose=args.verbose
        )
    elif args.command == "details":
        display_search_details(
            search_id=args.search_id,
            show_all=args.all
        )
    elif args.command == "export":
        export_search_to_json(
            search_id=args.search_id,
            output_file=args.output
        )
    elif args.command == "stats":
        get_statistics()
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
