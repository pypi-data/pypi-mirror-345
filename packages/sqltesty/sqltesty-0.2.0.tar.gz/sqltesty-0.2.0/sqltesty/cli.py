"""Command-line interface for sqltest."""

import sys
from pathlib import Path

import click

from .runner import run_sql_tests


@click.command()
@click.option(
    "--test-dir",
    default="tests/sqltest",
    help="Directory containing SQL test files and fixtures",
)
@click.option("--verbose", is_flag=True, help="Print detailed test information")
def main(test_dir: str, verbose: bool) -> int:
    """Run SQL tests against CSV fixtures using DuckDB."""
    test_path = Path(test_dir)
    if not test_path.exists():
        click.echo(f"Test directory not found: {test_path}", err=True)
        return 1

    success = run_sql_tests(test_path, verbose=verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
