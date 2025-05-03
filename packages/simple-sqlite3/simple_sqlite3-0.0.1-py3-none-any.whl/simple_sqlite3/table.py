# filepath: simple_sqlite/table.py
import sqlite3
import json
from typing import Any, Iterable, Optional, Union
from .exceptions import TableNotFoundError, InvalidDataError, SchemaMismatchError
import logging
from datetime import datetime

# Set up a logger for the Table class
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Default log level is WARNING

# Optional: Add a console handler only if explicitly enabled
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)


def enable_debug_logging():
    """
    Enables debug-level logging for the Table class.
    """
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(logging.DEBUG)

class Table:
    def __init__(self, connection_or_path: Union[sqlite3.Connection, str], name: str) -> None:
        """
        Initializes the Table object.

        Args:
            connection_or_path (sqlite3.Connection | str): SQLite connection or database path.
            name (str): Name of the table.
        """
        if isinstance(connection_or_path, str):
            self.connection = sqlite3.connect(connection_or_path)
        else:
            self.connection = connection_or_path
        self.cursor = self.connection.cursor()
        self.name = name
    
    def insert(self, data: Union[dict, Iterable[dict]], force: bool = True, schema: Optional[dict] = None) -> None:
        """
        Inserts data into the table. Automatically creates or updates the table schema if needed.
        Handles nested data structures by serializing them into JSON strings.
    
        Args:
            data (dict | Iterable[dict]): Data to insert.
            force (bool): Whether to add missing columns automatically. Defaults to True.
            schema (dict, optional): Exact schema for the data. If provided, skips schema inference.
        """
        logger.debug(f"Inserting data into table '{self.name}': {data}")
        if isinstance(data, dict):
            data = [data]
        if not all(isinstance(entry, dict) for entry in data):
            raise InvalidDataError("Data must be a dictionary or an iterable of dictionaries.")
    
        # Serialize nested structures into JSON strings
        def custom_serializer(obj):
            if isinstance(obj, datetime):  # Handle datetime objects
                return obj.strftime("%Y-%m-%d %H:%M:%S")  # SQLite-compatible format
            raise TypeError(f"Type {type(obj)} not serializable")
    
        for entry in data:
            for key, value in entry.items():
                if isinstance(value, (dict, list)):  # Serialize nested structures
                    entry[key] = json.dumps(value, default=custom_serializer)
    
        all_columns = {key for entry in data for key in entry.keys()}
        existing_columns = {col[1]: col[2] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")}
    
        if schema:
            # Use provided schema to create or update the table
            if not existing_columns:
                columns_def = ', '.join(f"{col} {schema[col]}" for col in schema)
                self.cursor.execute(f"CREATE TABLE {self.name} ({columns_def})")
            elif force:
                for col in schema.keys():
                    if col not in existing_columns:
                        self.cursor.execute(f"ALTER TABLE {self.name} ADD COLUMN {col} {schema[col]}")
        else:
            # Infer schema if not provided
            if not existing_columns:
                columns_def = ', '.join(f"{col} {self._infer_sqlite_type(data[0].get(col))}" for col in all_columns)
                self.cursor.execute(f"CREATE TABLE {self.name} ({columns_def})")
            elif force:
                for col in all_columns - existing_columns.keys():
                    self.cursor.execute(f"ALTER TABLE {self.name} ADD COLUMN {col} {self._infer_sqlite_type(data[0].get(col))}")
    
        # Insert the data
        for entry in data:
            columns = ', '.join(entry.keys())
            placeholders = ', '.join('?' * len(entry))
            self.cursor.execute(f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})", tuple(entry.values()))
        self.connection.commit()
        logger.info(f"Data inserted successfully into table '{self.name}'")
    
    def insert_batch(self, data: list[dict], force: bool = True) -> None:
        """
        Inserts multiple rows into the table in a single query, optimized for bulk operations.
    
        Args:
            data (list[dict]): A list of dictionaries representing rows to insert.
            force (bool): Whether to add missing columns automatically. Defaults to True.
        """
        logger.debug(f"Inserting bulk data into table '{self.name}': {data}")
        if not data or not isinstance(data, list) or not all(isinstance(entry, dict) for entry in data):
            raise InvalidDataError("Data must be a non-empty list of dictionaries.")
    
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join('?' * len(data[0]))
        values = [tuple(entry.values()) for entry in data]
    
        existing_columns = {col[1]: col[2] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")}
    
        # Infer schema if the table does not exist
        if not existing_columns:
            columns_def = ', '.join(f"{col} {self._infer_sqlite_type(data[0].get(col))}" for col in data[0].keys())
            self.cursor.execute(f"CREATE TABLE {self.name} ({columns_def})")
        elif force:
            # Add missing columns if force is True
            for col in data[0].keys():
                if col not in existing_columns:
                    self.cursor.execute(f"ALTER TABLE {self.name} ADD COLUMN {col} {self._infer_sqlite_type(data[0].get(col))}")
    
        # Insert the data
        self.cursor.executemany(f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})", values)
        self.connection.commit()
        logger.info(f"Bulk data inserted successfully into table '{self.name}'")
    
    def _flatten_dict(self, data: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Flattens a nested dictionary.
    
        Args:
            data (dict): The dictionary to flatten.
            parent_key (str): The base key string for recursion.
            sep (str): Separator for nested keys.
    
        Returns:
            dict: A flattened dictionary.
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def update(self, updates: dict, where: Optional[str] = None) -> None:
        """
        Updates records in the table.

        Args:
            updates (dict): A dictionary of column-value pairs to update. Complex data structures will be serialized.
            where (str, optional): A string specifying the WHERE clause to filter rows to update.

        Raises:
            ValueError: If updates is not a dictionary.
        """
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary of column-value pairs.")
    
        # Serialize complex data structures
        for key, value in updates.items():
            if isinstance(value, (list, dict, tuple, set)):
                updates[key] = json.dumps(value)
    
        # Build the SET clause
        set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
        params = list(updates.values())
    
        # Add the WHERE clause if provided
        query = f"UPDATE {self.name} SET {set_clause}"
        if where:
            query += f" WHERE {where}"
    
        # Execute the update query
        self.cursor.execute(query, params)
        self.connection.commit()

    def query(self, query: str, params: Optional[tuple] = None) -> list[dict]:
        """
        Executes a query and returns the raw results from SQLite.
        """
        logger.debug(f"Executing query: {query} with params: {params}")
        if "FROM" not in query.upper():
            parts = query.split("WHERE", 1)
            select_part = parts[0].strip()
            where_part = f"WHERE {parts[1]}" if len(parts) > 1 else ""
            if select_part.upper().startswith("SELECT"):
                query = f"{select_part} FROM {self.name} {where_part}".strip()
    
        try:
            self.cursor.execute(query, params or ())
            logger.info(f"Query executed successfully: {query}")
        except sqlite3.OperationalError as e:
            logger.error(f"Query failed: {query} - Error: {e}")
            if "no such table" in str(e):
                raise TableNotFoundError(f"Table '{self.name}' does not exist.")
            raise
    
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
    
        # Return raw results without deserialization
        return [dict(zip(columns, row)) for row in rows]

    def _infer_sqlite_type(self, value: Any) -> str:
        """
        Infers the SQLite data type for a given Python value.

        Args:
            value: The Python value to infer the type for.

        Returns:
            str: A string representing the SQLite data type.
        """
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        return "TEXT"

    def recalibrate(self, data: Optional[Union[dict, Iterable[dict]]] = None) -> None:
        """
        Recalibrates the table schema based on the provided data or existing data.

        Args:
            data (dict | Iterable[dict], optional): Optional data to infer the schema from.

        Raises:
            SchemaMismatchError: If the schema cannot be recalibrated due to conflicting types.
        """
        existing_columns = {col[1]: col[2] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")}
        all_columns = set(existing_columns.keys())
        if data:
            if isinstance(data, dict):
                data = [data]
            all_columns.update(key for entry in data for key in entry.keys())

        column_types = {}
        for column in all_columns:
            values = self.cursor.execute(f"SELECT {column} FROM {self.name} WHERE {column} IS NOT NULL").fetchall()
            inferred_types = {self._infer_sqlite_type(value[0]) for value in values if value}
            column_types[column] = "TEXT" if len(inferred_types) > 1 or not inferred_types else inferred_types.pop()

        for column, inferred_type in column_types.items():
            if column not in existing_columns:
                self.cursor.execute(f"ALTER TABLE {self.name} ADD COLUMN {column} {inferred_type}")
            elif existing_columns[column] != inferred_type:
                raise SchemaMismatchError(
                    f"Column '{column}' has a conflicting type. "
                    f"Expected: {existing_columns[column]}, Found: {inferred_type}"
                )
        self.connection.commit()

    def _rebuild_table(self, column: str, new_type: str) -> None:
        """
        Rebuilds the table to change the type of a column.

        Args:
            column (str): The column to modify.
            new_type (str): The new SQLite data type for the column.
        """
        column_definitions = [
            f"{col[1]} {new_type if col[1] == column else col[2]}"
            for col in self.cursor.execute(f"PRAGMA table_info({self.name})")
        ]
        temp_table = f"{self.name}_temp"
        self.cursor.execute(f"CREATE TABLE {temp_table} ({', '.join(column_definitions)})")
        self.cursor.execute(f"INSERT INTO {temp_table} SELECT * FROM {self.name}")
        self.cursor.execute(f"DROP TABLE {self.name}")
        self.cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {self.name}")

    def get_schema(self) -> list[tuple]:
        """
        Retrieves the schema of the table.

        Returns:
            list[tuple]: A list of tuples representing the table schema.
        """
        return self.cursor.execute(f"PRAGMA table_info({self.name})").fetchall()

    def rename_column(self, old_name: str, new_name: str) -> None:
        """
        Renames a column in the table.

        Args:
            old_name (str): The current name of the column.
            new_name (str): The new name for the column.
        """
        existing_columns = [col[1] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")]
        if old_name in existing_columns and new_name not in existing_columns:
            self.cursor.execute(f"ALTER TABLE {self.name} RENAME COLUMN {old_name} TO {new_name}")
            self.connection.commit()

    def drop_columns(self, *args: str) -> None:
        """
        Drops specified columns from the table.

        Args:
            *args (str): Column names to drop.
        """
        existing_columns = [col[1] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")]
        columns_to_keep = [col for col in existing_columns if col not in args]

        if not columns_to_keep:
            # If no columns remain, drop the table
            self.cursor.execute(f"DROP TABLE {self.name}")
            self.connection.commit()
            return

        temp_table = f"{self.name}_temp"
        column_definitions = [f"{col[1]} {col[2]}" for col in self.cursor.execute(f"PRAGMA table_info({self.name})") if col[1] in columns_to_keep]
        self.cursor.execute(f"CREATE TABLE {temp_table} ({', '.join(column_definitions)})")
        self.cursor.execute(f"INSERT INTO {temp_table} SELECT {', '.join(columns_to_keep)} FROM {self.name}")
        self.cursor.execute(f"DROP TABLE {self.name}")
        self.cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {self.name}")
        self.connection.commit()

    def keep_columns(self, *args: str) -> None:
        """
        Keeps only the specified columns in the table, dropping all others.

        Args:
            *args (str): Column names to keep.

        Raises:
            ValueError: If no valid columns to keep are provided.
        """
        existing_columns = [col[1] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")]
        columns_to_keep = [col for col in existing_columns if col in args]

        if not columns_to_keep:
            raise ValueError("No valid columns to keep were provided.")

        temp_table = f"{self.name}_temp"
        column_definitions = [
            f"{col[1]} {col[2]}"
            for col in self.cursor.execute(f"PRAGMA table_info({self.name})")
            if col[1] in columns_to_keep
        ]
        self.cursor.execute(f"CREATE TABLE {temp_table} ({', '.join(column_definitions)})")
        self.cursor.execute(f"INSERT INTO {temp_table} SELECT {', '.join(columns_to_keep)} FROM {self.name}")
        self.cursor.execute(f"DROP TABLE {self.name}")
        self.cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {self.name}")
        self.connection.commit()

    def delete_duplicates(self, by: Optional[list[str]] = None) -> None:
        """
        Deletes duplicate rows from the table.

        Args:
            by (list[str], optional): Optional list of column names to determine duplicates. Defaults to all columns.
        """
        if by is None:
            by = [col[1] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")]
        self.cursor.execute(f"""
            DELETE FROM {self.name}
            WHERE ROWID NOT IN (
                SELECT MIN(ROWID)
                FROM {self.name}
                GROUP BY {', '.join(by)}
            )
        """)
        self.connection.commit()

    def dropna(self, how: str = 'any', axis: int = 0) -> None:
        """
        Drops rows or columns with missing values (NULL).

        Args:
            how (str): 'any' (default) drops rows/columns with any NULL values, 'all' drops rows/columns where all values are NULL.
            axis (int): 0 (default) drops rows, 1 drops columns.

        Raises:
            ValueError: If invalid values are provided for 'how' or 'axis'.
        """
        if how not in ['any', 'all']:
            raise ValueError("Invalid value for 'how'. Use 'any' or 'all'.")
        if axis not in [0, 1]:
            raise ValueError("Invalid value for 'axis'. Use 0 (rows) or 1 (columns).")

        if axis == 0:  # Drop rows
            if how == 'any':
                conditions = " OR ".join(f"{col[1]} IS NULL" for col in self.cursor.execute(f"PRAGMA table_info({self.name})"))
                self.cursor.execute(f"DELETE FROM {self.name} WHERE {conditions}")
            else:  # how == 'all'
                conditions = " AND ".join(f"{col[1]} IS NULL" for col in self.cursor.execute(f"PRAGMA table_info({self.name})"))
                self.cursor.execute(f"DELETE FROM {self.name} WHERE {conditions}")
        else:  # Drop columns
            columns = [col[1] for col in self.cursor.execute(f"PRAGMA table_info({self.name})")]
            for col in columns:
                count_query = f"SELECT COUNT(*) FROM {self.name} WHERE {col} IS NOT NULL"
                count = self.cursor.execute(count_query).fetchone()[0]
                if (how == 'any' and count == 0) or (how == 'all' and count == 0):
                    self.drop_columns(col)

        self.connection.commit()

    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> None:
        """
        Executes a raw SQL query.

        Args:
            sql (str): The SQL query to execute.
            params (tuple, optional): Optional parameters for the query.
        """
        self.cursor.execute(sql, params or ())
        self.connection.commit()

    def backup(self, backup_name: str) -> None:
        """
        Creates a backup of the table by copying its data to a new table.

        Args:
            backup_name (str): The name of the backup table.
        """
        self.cursor.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {self.name}")
        self.connection.commit()

    def truncate(self) -> None:
        """Truncates the table by deleting all rows while keeping the structure intact."""
        self.cursor.execute(f"DELETE FROM {self.name}")
        self.connection.commit()

    def reset(self, confirm: bool = False) -> None:
        """
        Deletes all rows in the table while keeping the structure intact.

        Args:
            confirm (bool): If True, skips confirmation prompt. Defaults to False.

        Raises:
            ValueError: If confirmation is not provided.
        """
        if not confirm:
            logger.warning("Reset operation aborted: confirmation not provided.")
            raise ValueError("Confirmation required to reset the table. Pass confirm=True to proceed.")
        logger.info(f"Resetting table '{self.name}'")
        self.truncate()
        logger.info(f"Table '{self.name}' reset successfully")

    def delete(self, confirm: bool = False) -> None:
        """
        Deletes the table from the database.

        Args:
            confirm (bool): If True, skips confirmation prompt. Defaults to False.

        Raises:
            ValueError: If confirmation is not provided.
        """
        if not confirm:
            raise ValueError("Confirmation required to delete the table. Pass confirm=True to proceed.")
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.name}")
        self.connection.commit()
    
    def rename(self, new_name: str) -> None:
        """
        Renames the table.

        Args:
            new_name (str): The new name for the table.
        """
        self.cursor.execute(f"ALTER TABLE {self.name} RENAME TO {new_name}")
        self.connection.commit()
        self.name = new_name
        logger.info(f"Table renamed to '{new_name}'")

    def export_to_csv(self, file_path: str) -> None:
        """
        Exports the table's data to a CSV file.

        Args:
            file_path (str): Path to the CSV file.
        """
        import csv

        rows = self.query(f"SELECT * FROM {self.name}")
        if not rows:
            logger.warning(f"No data to export from table '{self.name}'")
            return

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"Data exported to CSV file: {file_path}")

    def export_to_json(self, file_path: str) -> None:
        """
        Exports the table's data to a JSON file.

        Args:
            file_path (str): Path to the JSON file.
        """
        rows = self.query(f"SELECT * FROM {self.name}")
        if not rows:
            logger.warning(f"No data to export from table '{self.name}'")
            return

        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(rows, file, indent=4)
        logger.info(f"Data exported to JSON file: {file_path}")