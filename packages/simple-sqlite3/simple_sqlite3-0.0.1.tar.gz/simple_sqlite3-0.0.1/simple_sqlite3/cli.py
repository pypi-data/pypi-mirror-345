import json
import argparse
import sqlite3
import os
from simple_sqlite3.table import Table
from typing import Optional

def main():
    parser = argparse.ArgumentParser(description="Command-line interface for SQLite database manipulation.")

    subparsers = parser.add_subparsers(dest="action", required=True, help="Database actions")

    # Remove the insert subparser
    # Subparser for querying records
    query_parser = subparsers.add_parser("query", help="Query records from a table")
    query_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    query_parser.add_argument("-table", required=True, help="Name of the table")
    query_parser.add_argument("-sql", required=True, help="SQL query to execute")

    # Subparser for deleting a database or a table
    delete_parser = subparsers.add_parser("delete", help="Delete a database or a specific table")
    delete_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    delete_parser.add_argument("-table", help="Name of the table to delete (optional)")

    # Subparser for renaming a column
    rename_column_parser = subparsers.add_parser("rename_column", help="Rename a column in a table")
    rename_column_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    rename_column_parser.add_argument("-table", required=True, help="Name of the table")
    rename_column_parser.add_argument("old_name", help="Current name of the column")
    rename_column_parser.add_argument("new_name", help="New name for the column")

    # Subparser for deleting a column
    delete_column_parser = subparsers.add_parser("delete_column", help="Delete a column from a table")
    delete_column_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    delete_column_parser.add_argument("-table", required=True, help="Name of the table")
    delete_column_parser.add_argument("column", help="Name of the column to delete")

    # Subparser for renaming a table
    rename_table_parser = subparsers.add_parser("rename_table", help="Rename a table")
    rename_table_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    rename_table_parser.add_argument("-table", required=True, help="Name of the table")
    rename_table_parser.add_argument("new_name", help="New name for the table")

    # Subparser for dropping duplicates
    drop_duplicates_parser = subparsers.add_parser("drop_duplicates", help="Drop duplicate rows from a table")
    drop_duplicates_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    drop_duplicates_parser.add_argument("-table", required=True, help="Name of the table")
    drop_duplicates_parser.add_argument("-by", nargs="+", help="Columns to check for duplicates (optional)")

    # Subparser for exporting data
    export_parser = subparsers.add_parser("export", help="Export table data to a file")
    export_parser.add_argument("-database", required=True, help="Path to the SQLite database")
    export_parser.add_argument("-table", required=True, help="Name of the table")
    export_parser.add_argument("-format", choices=["csv", "json"], required=True, help="Export format")
    export_parser.add_argument("-output", required=True, help="Output file path")

    args = parser.parse_args()

    # Remove the insert action handler
    if args.action == "query":
        query_records(args.database, args.table, args.sql)
    elif args.action == "delete":
        if args.table:
            delete_table(args.database, args.table)
        else:
            delete_database(args.database)
    elif args.action == "rename_column":
        rename_column(args.database, args.table, args.old_name, args.new_name)
    elif args.action == "delete_column":
        delete_column(args.database, args.table, args.column)
    elif args.action == "rename_table":
        rename_table(args.database, args.table, args.new_name)
    elif args.action == "drop_duplicates":
        drop_duplicates(args.database, args.table, args.by)
    elif args.action == "export":
        export_table(args.database, args.table, args.format, args.output)
    else:
        parser.print_help()

# Remove the insert_records function entirely

def query_records(database_path: str, table_name: str, sql: str):
    try:
        with sqlite3.connect(database_path) as conn:
            table = Table(conn, table_name)
            results = table.query(sql)
            if results:
                formatted_results = json.dumps(results, indent=4)
                print(formatted_results)
            else:
                print("No results found.")
    except Exception as e:
        print(f"Error querying records: {e}")

def delete_database(database_path: str):
    if os.path.exists(database_path):
        os.remove(database_path)
        print(f"Database '{database_path}' deleted.")
    else:
        print(f"Database '{database_path}' does not exist.")

def delete_table(database_path: str, table_name: str):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' deleted from database.")

def rename_column(database_path: str, table_name: str, old_name: str, new_name: str):
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.rename_column(old_name, new_name)
        print(f"Column '{old_name}' renamed to '{new_name}' in table '{table_name}'.")

def delete_column(database_path: str, table_name: str, column: str):
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.drop_columns(column)
        print(f"Column '{column}' deleted from table '{table_name}'.")

def rename_table(database_path: str, table_name: str, new_name: str):
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.rename(new_name)
        print(f"Table '{table_name}' renamed to '{new_name}'.")

def drop_duplicates(database_path: str, table_name: str, by: Optional[list[str]]):
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.delete_duplicates(by)
        print(f"Duplicates dropped from table '{table_name}' based on columns: {by}.")

def export_table(database_path: str, table_name: str, export_format: str, output_path: str):
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        if export_format == "csv":
            table.export_to_csv(output_path)
        elif export_format == "json":
            table.export_to_json(output_path)
        print(f"Table '{table_name}' exported to {export_format.upper()} at '{output_path}'.")