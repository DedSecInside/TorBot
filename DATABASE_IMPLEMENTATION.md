# Database Implementation Summary

## Overview

This document summarizes the implementation of database functionality for TorBot to save search results to a persistent SQLite database.

## Files Created

### 1. `src/torbot/modules/database.py`

**Purpose**: Core database module for handling SQLite operations

**Key Features**:

- `SearchResultsDatabase` class that manages SQLite database connections
- Automatic database initialization with two tables:
  - `searches`: Stores metadata about each crawl operation
  - `links`: Stores detailed information about discovered links
- Methods:
  - `save_search_results()`: Persist search results to database
  - `get_search_history()`: Retrieve search records with optional filtering
  - `get_search_by_id()`: Get detailed information about a specific search
  - `close()`: Properly close database connections

**Stored Metadata**:

- Root URL
- Search timestamp (ISO format)
- Crawl depth
- Total links found
- For each link:
  - URL and page title
  - HTTP status code
  - Content classification and accuracy
  - Email addresses found
  - Phone numbers found

### 2. `src/torbot/modules/db_query.py`

**Purpose**: Utility functions for querying and displaying database results

**Key Functions**:

- `display_search_history()`: Show search history with optional filtering
- `display_search_details()`: Display comprehensive information about a specific search
- `export_search_to_json()`: Export search results to JSON file
- `get_statistics()`: Show database statistics

### 3. `scripts/query_database.py`

**Purpose**: Command-line interface for database operations

**Supported Commands**:

- `history`: View search history
- `details`: View specific search details
- `export`: Export search to JSON
- `stats`: Show database statistics

## Files Modified

### 1. `main.py`

**Changes**:

- Updated `--save` argument choices to include "database"
- Added handler in `run()` function to call `tree.saveDatabase()` when `--save database` is specified

### 2. `src/torbot/modules/linktree.py`

**Changes**:

- Added import for `SearchResultsDatabase`
- Implemented `saveDatabase()` method that:
  - Extracts all nodes from the tree
  - Formats link data with complete metadata
  - Saves to database
  - Displays save confirmation and statistics

### 3. `README.md`

**Changes**:

- Updated Features section to indicate database support is complete
- Updated Options section to include "database" as a `--save` option
- Updated Curated Features checklist to mark database feature as complete

## Files Created (Documentation)

### 1. `docs/DATABASE.md`

Comprehensive documentation including:

- Overview of database features
- Usage instructions
- Database schema documentation
- Python API examples
- Use cases
- Troubleshooting guide
- Complete workflow examples

### 2. `DATABASE_IMPLEMENTATION.md`

This file, summarizing the implementation

## Database Features

### Core Functionality

1. **Persistent Storage**: SQLite database stores all search results
2. **Timestamp Tracking**: Records exact time of each search
3. **Rich Metadata**: Captures HTTP status, classifications, contact info
4. **Search History**: Query and filter previous searches
5. **Export Capability**: Convert database records to JSON

### Data Captured

Each search record contains:

- Root URL
- Search timestamp (ISO 8601 format)
- Crawl depth
- Total links count
- For each discovered link:
  - URL and page title
  - HTTP status code
  - Content classification (from NLP module)
  - Classification confidence score
  - Email addresses found
  - Phone numbers found

### Query Capabilities

- View search history with optional URL filtering
- Retrieve detailed information about specific searches
- Export searches to JSON format
- View aggregate statistics
- Filter results by date range (via history)

## Usage Examples

### Save search results to database

```bash
python main.py -u http://example.onion --depth 2 --save database
```

### View search history

```bash
python scripts/query_database.py history
python scripts/query_database.py history -u http://example.onion -v
```

### View detailed search results

```bash
python scripts/query_database.py details 1 --all
```

### Export results

```bash
python scripts/query_database.py export 1 -o search_results.json
```

### View statistics

```bash
python scripts/query_database.py stats
```

## Technical Details

### Database Location

- Default: `<project_root>/torbot_search_results.db`
- SQLite format (no external database server required)
- Single file makes backup/migration easy

### Database Schema

#### Searches Table

- id: Auto-incrementing primary key
- root_url: The URL that was crawled
- search_timestamp: ISO 8601 timestamp
- depth: Crawl depth setting
- total_links: Count of discovered links
- links_data: JSON serialized link details
- created_at: Record creation timestamp

#### Links Table

- id: Auto-incrementing primary key
- search_id: Foreign key to searches
- url: Full URL of discovered link
- title: Page title or hostname
- status_code: HTTP status code
- classification: Content category
- accuracy: Classification confidence (0.0-1.0)
- emails: JSON array of emails
- phone_numbers: JSON array of phone numbers

### Dependencies

- Python 3.7+
- sqlite3 (built-in to Python)
- tabulate (already in project dependencies)

## Benefits

1. **Persistence**: Search results survive between program runs
2. **Historical Analysis**: Track how sites and links change over time
3. **Searchability**: Query results by URL, date, or other criteria
4. **Export**: Convert data to JSON for other tools
5. **Accountability**: Maintain audit trail of all searches
6. **No External Services**: SQLite requires no server setup

## Future Enhancements

Potential improvements for future versions:

- PostgreSQL support for multi-user environments
- Encryption for sensitive data
- Automated database cleanup/archival
- Web-based query interface
- Advanced filtering and search capabilities
- Full-text search on page titles and URLs
- Duplicate detection across searches
- Relationship visualization

## Testing Notes

The implementation:

- Uses built-in sqlite3 module (no external dependencies needed)
- Automatically creates database and tables on first run
- Handles errors gracefully with logging
- Properly closes database connections
- Validates all input data

## Integration Points

The database functionality integrates with:

1. **LinkTree class**: Extracts link data and calls `saveDatabase()`
2. **Main execution flow**: Triggered via `--save database` flag
3. **Database utility**: Separate tools for querying and analysis

## File Tree

```
TorBot/
├── main.py (MODIFIED)
├── docs/
│   └── DATABASE.md (NEW)
├── src/torbot/modules/
│   ├── linktree.py (MODIFIED)
│   ├── database.py (NEW)
│   └── db_query.py (NEW)
├── scripts/
│   └── query_database.py (NEW)
└── DATABASE_IMPLEMENTATION.md (NEW)
```

## Deployment Notes

1. No additional Python packages needed (sqlite3 is built-in)
2. Database file is created automatically on first use
3. No configuration required - works out of the box
4. Backward compatible with existing code
5. Safe to enable alongside existing save formats

## Support and Documentation

Users can refer to:

- `docs/DATABASE.md` for comprehensive feature documentation
- `scripts/query_database.py --help` for command-line options
- Inline code documentation in modules for Python API usage
