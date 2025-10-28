# TorBot Database Feature

## Overview

TorBot now includes a built-in SQLite database for persisting search results. This allows you to save and query crawled links, metadata, and search history without losing data between sessions.

## Features

- **Persistent Storage**: Search results are saved to a local SQLite database
- **Comprehensive Metadata**: Each search record includes:
  - Root URL
  - Search timestamp
  - Crawl depth
  - Total links found
  - Detailed information for each link:
    - URL and title
    - HTTP status code
    - Content classification
    - Classification accuracy
    - Email addresses found
    - Phone numbers found
- **Search History**: Track all your searches over time
- **Query Tools**: Command-line utilities to view and export saved searches

## Basic Usage

### Saving Results to Database

To save your crawl results to the database, use the `--save database` flag:

```bash
python main.py -u http://example.onion --depth 2 --save database
```

This will:

1. Crawl the specified URL to the given depth
2. Extract all links and metadata
3. Save everything to `torbot_search_results.db` in your project directory

### Database Location

By default, the database is created in your TorBot project root directory:

```
<project_root>/torbot_search_results.db
```

## Querying Search Results

The `query_database.py` script provides a command-line interface for accessing your saved search data.

### Available Commands

#### 1. View Search History

```bash
python scripts/query_database.py history
```

Shows the last 10 searches with basic information:

- Search ID
- Root URL
- Timestamp
- Crawl depth
- Total links found

**Options:**

- `-u, --url <URL>`: Filter by specific root URL
- `-l, --limit <N>`: Show last N records (default: 10)
- `-v, --verbose`: Show detailed information

**Example:**

```bash
python scripts/query_database.py history -u http://example.onion -l 5
```

#### 2. View Search Details

```bash
python scripts/query_database.py details <SEARCH_ID>
```

Displays detailed information about a specific search, including a summary table of all discovered links.

**Options:**

- `-a, --all`: Show all links in detailed format instead of summary table

**Example:**

```bash
python scripts/query_database.py details 1 --all
```

#### 3. Export Search Results

```bash
python scripts/query_database.py export <SEARCH_ID> -o <OUTPUT_FILE>
```

Exports a specific search to a JSON file for further processing or backup.

**Example:**

```bash
python scripts/query_database.py export 1 -o my_search.json
```

#### 4. View Database Statistics

```bash
python scripts/query_database.py stats
```

Shows overall statistics:

- Total searches performed
- Unique root URLs crawled
- Total links found across all searches
- Average links per search
- Average crawl depth

## Database Schema

### Searches Table

Stores information about each crawl operation:

| Column           | Type     | Description                             |
| ---------------- | -------- | --------------------------------------- |
| id               | INTEGER  | Primary key, auto-incremented           |
| root_url         | TEXT     | The root URL that was crawled           |
| search_timestamp | DATETIME | When the search was performed           |
| depth            | INTEGER  | Crawl depth used                        |
| total_links      | INTEGER  | Number of links discovered              |
| links_data       | TEXT     | JSON array of detailed link information |
| created_at       | DATETIME | When the record was inserted            |

### Links Table

Stores detailed information about each discovered link:

| Column         | Type    | Description                        |
| -------------- | ------- | ---------------------------------- |
| id             | INTEGER | Primary key, auto-incremented      |
| search_id      | INTEGER | Foreign key to searches table      |
| url            | TEXT    | Link URL                           |
| title          | TEXT    | Page title or hostname             |
| status_code    | INTEGER | HTTP status code                   |
| classification | TEXT    | Content category classification    |
| accuracy       | REAL    | Classification accuracy score      |
| emails         | TEXT    | JSON array of emails found on page |
| phone_numbers  | TEXT    | JSON array of phone numbers found  |

## Python API

You can also interact with the database programmatically:

### Basic Usage

```python
from torbot.modules.database import SearchResultsDatabase

# Initialize database
db = SearchResultsDatabase()

# Prepare your links data
links_data = [
    {
        "url": "http://example.onion/page1",
        "title": "Page 1",
        "status": 200,
        "classification": "marketplace",
        "accuracy": 0.95,
        "emails": ["contact@example.com"],
        "phone_numbers": ["+1234567890"]
    },
    # ... more links
]

# Save search results
search_id = db.save_search_results(
    root_url="http://example.onion",
    depth=2,
    links_data=links_data
)

print(f"Search saved with ID: {search_id}")

# Close database connection
db.close()
```

### Query Database

```python
from torbot.modules.database import SearchResultsDatabase

db = SearchResultsDatabase()

# Get search history
history = db.get_search_history(limit=10)
for record in history:
    print(f"ID: {record['id']}, URL: {record['root_url']}")

# Get specific search with full details
search = db.get_search_by_id(1)
print(f"Found {len(search['links_data'])} links")
for link in search['links_data']:
    print(f"  - {link['title']}: {link['url']}")

db.close()
```

## Use Cases

### 1. OSINT Research

Maintain a comprehensive database of your dark web reconnaissance activities, searchable by URL, date, and content type.

### 2. Threat Intelligence

Track changes in discovered links and their classifications over time to identify emerging threats.

### 3. Historical Analysis

Compare crawl results across different dates to understand how sites and link networks evolve.

### 4. Data Export

Export specific searches for analysis in external tools, reports, or data visualization platforms.

### 5. Audit Trail

Maintain a complete record of all your searches with timestamps for accountability and reproducibility.

## Performance Considerations

- The database uses SQLite, which is lightweight and requires no external server
- Database size grows with the number of searches and links stored
- For large-scale operations (thousands of searches), consider archiving old records
- Queries are typically fast for reasonably-sized databases (< 1GB)

## Backup and Maintenance

### Backup Your Database

```bash
# Copy the database file
cp torbot_search_results.db torbot_search_results.backup.db
```

### Export All Data

```bash
# Export everything to JSON
python scripts/query_database.py history --limit 9999 > all_searches.txt
```

### Managing Database Size

Monitor your database file size and archive old searches if needed:

```bash
ls -lh torbot_search_results.db
```

## Limitations and Future Improvements

- Currently uses SQLite; consider PostgreSQL for multi-user environments
- No built-in data encryption; consider encrypting sensitive data
- No automatic cleanup; manually manage old records
- Search queries are limited to command-line interface; could add web interface
- No authentication; keep database file secure

## Troubleshooting

### Database file not found

Make sure you're running TorBot from the project root directory:

```bash
cd /path/to/TorBot
python main.py -u http://example.onion --save database
```

### Permission denied errors

Ensure you have write permissions to the project root directory:

```bash
chmod 755 /path/to/TorBot
```

### Query returns no results

Check that:

1. You've run at least one search with `--save database`
2. The search ID you're querying actually exists
3. The database file hasn't been moved

## Examples

### Complete Workflow

```bash
# 1. Crawl a dark web site and save to database
python main.py -u http://example.onion --depth 2 --save database

# 2. View all searches
python scripts/query_database.py history

# 3. View details of a specific search
python scripts/query_database.py details 1

# 4. Export for further analysis
python scripts/query_database.py export 1 -o search_1_results.json

# 5. View statistics
python scripts/query_database.py stats
```

### Python Integration Example

```python
#!/usr/bin/env python3
from torbot.modules.database import SearchResultsDatabase
from torbot.modules.db_query import display_search_history, get_statistics

# Display all searches
display_search_history(verbose=True)

# Get statistics
get_statistics()

# Export search 1 to JSON
export_search_to_json(1, "exported_search.json")
```

## Contributing

If you have suggestions for improving the database feature, please open an issue or submit a pull request!
