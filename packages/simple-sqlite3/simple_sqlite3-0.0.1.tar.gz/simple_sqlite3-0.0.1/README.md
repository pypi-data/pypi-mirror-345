# Simple SQLite3

Simple SQLite3 is a lightweight Python library that provides a simple and intuitive wrapper for working with SQLite3 databases. It includes features for managing tables, querying data, and performing common database operations.

## Features

- Easy-to-use API for SQLite3 database and table management.
- Command-line interface (CLI) for database operations.
- Support for exporting data to CSV and JSON formats.
- Utilities for querying results.

## Installation

Install the library using pip:

```bash
pip install simple-sqlite3
```

## Usage

Programmatic Usage

```bash
from simple_sqlite3 import Database

# Create or connect to a database
db = Database("database.db")

# Create a table
table = db.table("tab")

# Insert data
table.insert([
    {"letter": "A", "order": 1},
    {"letter": "B", "order": 2},
])

# Query data
results = table.query("SELECT *")
print(results)
```

Command-Line Interface (CLI)

- Query a table:
```bash
db query -database database.db -table tab -sql "SELECT *"
```

- Delete a table:
```bash
db delete -database database.db -table tab
```

- Export a table to CSV:
```bash
db export -database database.db -table tab -format csv -output output.csv
```

For a full list of commands, run:
```bash
db --help
```

## License
This project is developed by Rob Suomi and licensed under the MIT License. See the LICENSE file for details.