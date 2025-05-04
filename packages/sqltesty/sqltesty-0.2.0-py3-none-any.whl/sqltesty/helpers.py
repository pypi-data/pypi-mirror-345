import re
from pathlib import Path

import click
import duckdb
import pandas as pd

TableMapping = dict[str, pd.DataFrame]


def extract_order_by_columns(sql_query: str) -> list[str]:
    """
    Extract all columns from the ORDER BY clause of an SQL query, considering renamed columns in
    the SELECT statement. If columns are prefixed with a table name (e.g., table1.column),
    only the column name is returned unless renamed.
    """
    # Regex to match the SELECT and ORDER BY clauses (supporting multi-line strings)
    select_pattern = r"(?is)select\s+(.*?)\s+from"
    order_by_pattern = r"(?is)order\s+by\s+([\w\s,\.\[\]\"'`]+)"

    # Extract SELECT clause
    select_match = re.search(select_pattern, sql_query)
    if not select_match:
        return []  # No SELECT clause found

    select_clause = select_match.group(1)

    # Map original column names to renamed names
    column_alias_map = {}
    for part in select_clause.split(","):
        strip_part = part.strip()
        if " as " in part.lower():
            original, alias = re.split(r"(?i)\s+as\s+", strip_part)
            column_alias_map[original.strip()] = alias.strip()
        else:
            # Handle table-prefixed columns (e.g., table1.column)
            column_name = strip_part.split(".")[-1].strip()
            column_alias_map[column_name] = column_name

    # Extract ORDER BY clause
    order_by_match = re.search(order_by_pattern, sql_query)
    if not order_by_match:
        return []  # No ORDER BY clause found

    order_by_clause = order_by_match.group(1)

    # Split by commas and clean up ASC/DESC and whitespace
    columns = []
    for col in order_by_clause.split(","):
        sub_col = re.sub(r"\s+(asc|desc)$", "", col.strip(), flags=re.IGNORECASE)
        # Remove table prefix if present
        col_name = sub_col.split(".")[-1]

        cleaned_name = column_alias_map.get(col_name)
        if cleaned_name is None:
            cleaned_name = column_alias_map.get(sub_col, col_name)

        # Use alias if available
        columns.append(cleaned_name)

    return columns


def load_csv_files(
    table_files: list[Path], sql_file: Path, verbose: bool
) -> tuple[TableMapping, str]:
    tables: TableMapping = {}

    for table_file in table_files:
        table_name = table_file.stem
        if verbose:
            click.echo(f"  Loading table: {table_name}")
        tables[table_name] = pd.read_csv(table_file)

    with open(sql_file) as f:
        sql_query = f.read()

    return tables, sql_query


def run_query_duckdb(tables: TableMapping, sql_query: str) -> pd.DataFrame:
    conn = duckdb.connect(":memory:")

    for table_name, result in tables.items():
        conn.register(table_name, result)

    return conn.execute(sql_query).fetchdf()
