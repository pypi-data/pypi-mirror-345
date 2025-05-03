"""Core test runner for SQL tests."""

from pathlib import Path

import click
import duckdb
import pandas as pd

from .output_formatter import (
    format_success_message,
    format_error_message,
    format_dataframe_diff,
    format_test_summary,
)


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize a DataFrame for consistent comparison.

    This function:
    1. Resets the index
    2. Converts numeric columns to float for consistent comparison
    3. Sorts rows by all columns for consistent ordering
    """
    # Create a copy to avoid modifying the original
    result = df.copy()

    # Convert numeric columns to float
    for col in result.select_dtypes(include=["number"]).columns:
        result[col] = result[col].astype(float)

    # Try to sort by all columns to ensure consistent order
    try:
        result = result.sort_values(by=list(result.columns))
    except Exception:
        # If sorting fails (e.g., due to mixed types), just continue
        pass

    # Reset index AFTER sorting
    return result.reset_index(drop=True)


TableMapping = dict[str, pd.DataFrame]


def load_csv_files(
    table_files: list[Path], sql_file: Path, verbose: bool
) -> tuple[TableMapping, str]:
    tables: TableMapping = {}

    for table_file in table_files:
        table_name = table_file.stem
        if verbose:
            click.echo(f"  Loading table: {table_name}")
        tables[table_name] = pd.read_csv(table_file)

    with open(sql_file, "r") as f:
        sql_query = f.read()

    return tables, sql_query


def run_query_duckdb(
    tables: TableMapping, sql_query: str, verbose: bool
) -> pd.DataFrame:
    conn = duckdb.connect(":memory:")

    for table_name, result in tables.items():
        conn.register(table_name, result)

    result = conn.execute(sql_query).fetchdf()
    if "order by" in sql_query.lower():
        try:
            result = result.sort_values(by=list(result.columns))
            if verbose:
                click.echo(
                    "No ORDER BY in SQL: Data ordered by columns from left to right"
                )
        except Exception:
            if verbose:
                click.echo("No ORDER BY in SQL: Ordering FAILED!!!")
            # If sorting fails (e.g., due to mixed types), just continue
            pass

    return result


def run_sql_test(sql_file: Path, test_dir: Path, verbose: bool = False) -> bool:
    """Run a single SQL test against its fixture data.

    Args:
        sql_file: Path to the SQL file to test
        test_dir: Path to the directory containing test fixtures
        verbose: Whether to print detailed output

    Returns:
        True if the test passed, False otherwise
    """
    if verbose:
        click.echo(f"Testing {sql_file.relative_to(sql_file.parent.parent)}")

    # Find the test directory for this SQL file
    test_name = sql_file.stem
    fixture_dir = test_dir / test_name

    if not fixture_dir.exists():
        click.echo(f"Error: No test fixtures found for {test_name}", err=True)
        return False

    # Find and load table CSV files
    table_files = [f for f in fixture_dir.glob("*.csv") if f.name != "output.csv"]
    output_file = fixture_dir / "output.csv"

    if not output_file.exists():
        click.echo(f"Error: No output.csv found for {test_name}", err=True)
        return False

    if not table_files:
        click.echo(f"Error: No table CSV files found for {test_name}", err=True)
        return False

    tables, sql_query = load_csv_files(table_files, sql_file, verbose)

    try:
        actual_result = run_query_duckdb(tables, sql_query, verbose)
    except Exception as e:
        click.echo(f"Error executing SQL for {test_name}: {e}", err=True)
        return False

    # Load expected output
    expected_result = pd.read_csv(output_file)

    # Normalize both DataFrames for more consistent comparison
    actual_norm = normalize_dataframe(actual_result)
    expected_norm = normalize_dataframe(expected_result)

    # Compare results with more flexible comparison
    try:
        # First check that we have the same columns
        if set(actual_norm.columns) != set(expected_norm.columns):
            raise AssertionError(
                f"Column mismatch: {set(actual_norm.columns)} != {set(expected_norm.columns)}"
            )

        # Then check that we have the same number of rows
        if len(actual_norm) != len(expected_norm):
            raise AssertionError(
                f"Row count mismatch: {len(actual_norm)} != {len(expected_norm)}"
            )

        # For each column, check that the sorted values match
        for col in actual_norm.columns:
            if (
                not actual_norm[col]
                .sort_values()  # type: ignore
                .reset_index(drop=True)
                .equals(expected_norm[col].sort_values().reset_index(drop=True))  # type: ignore
            ):
                raise AssertionError(
                    f"Values in column '{col}' don't match after sorting"
                )

        if verbose:
            format_success_message(test_name)
        return True
    except AssertionError as e:
        error_message = str(e)
        error_type = (
            error_message.split(":")[0] if ":" in error_message else "Assertion Error"
        )

        if not verbose:
            click.echo(f"✗ Test failed: {test_name}", err=True)
        else:
            format_error_message(test_name, error_type, error_message)
            format_dataframe_diff(expected_result, actual_result)
        return False


def run_sql_tests(test_dir: Path, verbose: bool = False) -> bool:
    """Run all SQL tests in the specified directory.

    Args:
        test_dir: Directory containing SQL test files and fixtures
        verbose: Whether to print detailed output

    Returns:
        True if all tests passed, False otherwise
    """
    # Find all SQL files in the repo (parent directory of test_dir)
    repo_dir = test_dir.parent.parent if test_dir.name == "sqltest" else test_dir.parent
    sql_files = list(repo_dir.glob("**/*.sql"))

    if not sql_files:
        click.echo("No SQL files found to test", err=True)
        return False

    # Run tests for each SQL file
    results = []
    for sql_file in sql_files:
        results.append(run_sql_test(sql_file, test_dir, verbose))

    # Print summary
    total = len(results)
    passed = sum(results)
    failed = total - passed

    # Use the enhanced formatter for the summary
    format_test_summary(total, passed)

    return failed == 0
