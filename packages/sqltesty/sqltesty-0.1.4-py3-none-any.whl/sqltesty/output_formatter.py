"""Output formatting utilities for SQL test results."""

from typing import Set

import pandas as pd
from rich.console import Console
from rich.table import Table

EMPTY_FIELD = "-"

# Create a console for rich output
console = Console()


def format_success_message(test_name: str) -> None:
    """Format and display a success message for a passed test."""
    console.print(f"[bold green]✓[/bold green] Test passed: {test_name}")


def format_error_message(test_name: str, error_type: str, error_details: str) -> None:
    """Format and display an error message for a failed test."""
    console.print(f"[bold red]✗[/bold red] Test failed: {test_name}", highlight=False)
    console.print(f"  Error type: [yellow]{error_type}[/yellow]")
    console.print(f"  {error_details}")


def format_column_mismatch(expected_cols: Set[str], actual_cols: Set[str]) -> None:
    """Format and display column mismatches between expected and actual DataFrames."""
    missing_cols = sorted(expected_cols - actual_cols)
    extra_cols = sorted(actual_cols - expected_cols)
    common_cols = sorted(expected_cols & actual_cols)

    console.print("\n[bold]Column Differences:[/bold]")

    if missing_cols:
        console.print(f"  [red]- Missing:[/red] {list(missing_cols)}")

    if extra_cols:
        console.print(f"  [yellow]+ Extra:[/yellow] {list(extra_cols)}")

    if common_cols:
        console.print(f"  [green]  Common:[/green] {len(common_cols)} columns")


def format_row_count_mismatch(expected_count: int, actual_count: int) -> None:
    """Format and display row count mismatches between expected and actual DataFrames."""
    console.print("\n[bold]Row Count Mismatch:[/bold]")
    console.print(f"  Expected: [green]{expected_count}[/green] rows")
    console.print(f"  Actual: [red]{actual_count}[/red] rows")

    if expected_count > actual_count:
        console.print(f"  [red]Missing {expected_count - actual_count} rows[/red]")
    else:
        console.print(f"  [yellow]Extra {actual_count - expected_count} rows[/yellow]")


def create_formatted_row(
    all_cols: list[str], diff_info: dict[str, str], row: pd.Series
):
    expected_data = []
    for col in all_cols:
        col_status = diff_info.get(col)
        # Safely access value only if row and column exist
        if row is not None and col in row.index:
            value = str(row[col])
        else:
            value = EMPTY_FIELD  # Default if column doesn't exist in this row

        if col_status == "diff":
            expected_data.append(f"[on red]{value}[/]")
        elif col_status == "extra":  # Column exists in Expected, not Actual
            expected_data.append(f"[on yellow]{value}[/]")
        elif col_status == "missing":  # Column exists in Actual, not Expected
            expected_data.append(f"[dim]{EMPTY_FIELD}[/]")  # Placeholder
        else:  # match
            expected_data.append(value)

    return expected_data


def format_row_based_diff(expected_df: pd.DataFrame, actual_df: pd.DataFrame) -> None:
    """Format and display differences between DataFrames based on row indices.

    Compares rows with matching indices. If differences are found, prints the
    row twice (Expected and Actual) vertically, highlighting differing columns.
    Rows without differences are skipped. Handles rows present only in one DataFrame.
    """
    found_differences = False
    all_indices = sorted(list(set(expected_df.index) | set(actual_df.index)))
    expected_cols = set(expected_df.columns)
    actual_cols = set(actual_df.columns)
    all_cols = list(expected_df.columns) + sorted(actual_cols - expected_cols)

    table = Table(show_header=True, header_style="bold magenta", padding=(0, 1))
    found_differences = True
    table.add_column("Row ID", style="bold cyan", width=8)
    table.add_column("Type", width=10)
    for col in all_cols:
        table.add_column(col)

    for idx in all_indices:
        expected_row_exists = idx in expected_df.index
        actual_row_exists = idx in actual_df.index

        expected_row = expected_df.loc[idx] if expected_row_exists else None
        actual_row = actual_df.loc[idx] if actual_row_exists else None

        diff_info: dict[str, str] = {}  # Store diff status per column for this row
        has_row_diff = False

        # Determine differences for columns present in both
        common_cols = expected_cols & actual_cols
        for col in common_cols:
            diff_info[col] = "match"
            if (
                expected_row is not None
                and actual_row is not None
                and expected_row[col] != actual_row[col]
            ):
                diff_info[col] = "diff"
                has_row_diff = True

        # Mark columns only in expected as 'extra'
        for col in expected_cols - actual_cols:
            diff_info[col] = "extra"  # Expected has it, Actual doesn't
            has_row_diff = True

        # Mark columns only in actual as 'missing'
        for col in actual_cols - expected_cols:
            diff_info[col] = "missing"  # Actual has it, Expected doesn't
            has_row_diff = True

        # If row only exists in one df, mark it as a difference
        if not expected_row_exists or not actual_row_exists:
            has_row_diff = True

        if not has_row_diff:
            continue

        # --- Expected Row ---
        if expected_row_exists:
            expected_data = [
                f"[bold cyan]{idx}[/]",
                "[green]Expected[/]",
            ] + create_formatted_row(all_cols, diff_info, expected_row)  # type: ignore
            table.add_row(*expected_data)
        else:
            # Indicate Expected row is missing entirely for this index
            table.add_row(
                f"[bold cyan]{idx}[/]",
                "[red]Expected[/]",
                "[dim]Row not found[/]",
                *([f"[dim]{EMPTY_FIELD}[/]"] * (len(all_cols) - 1)),
            )

        # --- Actual Row ---
        if actual_row_exists:
            actual_data = ["", "[red]Actual[/]"] + create_formatted_row(
                all_cols,
                diff_info,
                actual_row,  # type: ignore
            )
            table.add_row(*actual_data, end_section=True)
        else:
            # Indicate Actual row is missing entirely for this index
            table.add_row(
                "",
                "[red]Actual[/]",
                "[dim]Row not found[/]",
                *([f"[dim]{EMPTY_FIELD}[/]"] * (len(all_cols) - 1)),
                end_section=True,
            )

    console.print(table)
    if not found_differences:
        console.print("\n[green]No row-based differences found.[/green]")


def format_dataframe_diff(expected_df: pd.DataFrame, actual_df: pd.DataFrame) -> None:
    """Formats and displays the differences between expected and actual DataFrames.

    Handles column and row count mismatches first, then delegates to
    format_row_based_diff for detailed, vertically stacked row comparisons.
    """
    console.print("\n[bold]Comparing DataFrames:[/bold]")

    # Check if columns match
    expected_cols = set(expected_df.columns)
    actual_cols = set(actual_df.columns)
    column_mismatch = expected_cols != actual_cols
    if column_mismatch:
        format_column_mismatch(expected_cols, actual_cols)

    # Check if row counts match
    row_count_mismatch = len(expected_df) != len(actual_df)
    if row_count_mismatch:
        format_row_count_mismatch(len(expected_df), len(actual_df))

    # Perform the detailed row-based comparison
    console.print("\n[bold]Detailed Row Comparison:[/bold]")
    # Use original indices if they exist and are meaningful.
    # The runner.py normalization step resets index after sorting,
    # so using the DataFrame index directly should be fine here.
    format_row_based_diff(expected_df, actual_df)


def format_test_summary(total: int, passed: int) -> None:
    """Format and display a summary of test results."""
    failed = total - passed

    if failed == 0:
        console.print(f"\n[bold green]✓ All {total} tests passed![/bold green]")
    else:
        console.print(f"\n[bold red]✗ {failed} of {total} tests failed.[/bold red]")

    # Add a visual representation of pass/fail ratio
    if total > 0:
        pass_percent = (passed / total) * 100
        bar_width = 40
        pass_width = int((pass_percent / 100) * bar_width)
        fail_width = bar_width - pass_width

        bar = f"[green]{'█' * pass_width}[/green][red]{'█' * fail_width}[/red]"
        console.print(f"\n{bar} {pass_percent:.1f}% passed")
