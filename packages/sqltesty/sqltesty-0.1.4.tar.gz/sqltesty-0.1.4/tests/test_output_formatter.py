"""Tests for the output formatter module."""

import io
from unittest.mock import patch

import pandas as pd
import pytest

from sqltesty.output_formatter import (
    format_success_message,
    format_error_message,
    format_column_mismatch,
    format_row_count_mismatch,
    format_row_based_diff,
    format_dataframe_diff,
    format_test_summary,
)


@pytest.fixture
def sample_dataframes():
    """Create sample DataFrames for testing."""
    # Expected DataFrame
    expected_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.5, 20.0, 30.5],
        }
    )

    # Actual DataFrame with some differences
    actual_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bobby", "Charlie"],  # Difference in name
            "value": [10.5, 25.0, 30.5],  # Difference in value
        }
    )

    return expected_df, actual_df


@pytest.fixture
def column_mismatch_dataframes():
    """Create DataFrames with column mismatches."""
    # Expected DataFrame
    expected_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.5, 20.0, 30.5],
        }
    )

    # Actual DataFrame with different columns
    actual_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "full_name": ["Alice", "Bob", "Charlie"],  # Different column name
            "score": [10.5, 20.0, 30.5],  # Different column name
        }
    )

    return expected_df, actual_df


@pytest.fixture
def row_count_mismatch_dataframes():
    """Create DataFrames with row count mismatches."""
    # Expected DataFrame
    expected_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.5, 20.0, 30.5],
        }
    )

    # Actual DataFrame with fewer rows
    actual_df = pd.DataFrame(
        {
            "id": [1, 2],
            "name": ["Alice", "Bob"],
            "value": [10.5, 20.0],
        }
    )

    return expected_df, actual_df


def test_format_success_message(snapshot):
    """Test formatting a success message."""
    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        format_success_message("test_query")
        output = fake_out.getvalue()

    assert output == snapshot


def test_format_error_message(snapshot):
    """Test formatting an error message."""
    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        format_error_message(
            "test_query",
            "Column mismatch",
            "Expected columns don't match actual columns",
        )
        output = fake_out.getvalue()

    assert output == snapshot


def test_format_column_mismatch(snapshot):
    """Test formatting column mismatches."""
    expected_cols = {"id", "name", "value"}
    actual_cols = {"id", "full_name", "score"}

    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        format_column_mismatch(expected_cols, actual_cols)
        output = fake_out.getvalue()

    assert output == snapshot


def test_format_row_count_mismatch(snapshot):
    """Test formatting row count mismatches."""
    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        format_row_count_mismatch(3, 2)
        output = fake_out.getvalue()

    assert output == snapshot


def test_format_row_based_diff(sample_dataframes, snapshot):
    """Test formatting row-based differences."""
    expected_df, actual_df = sample_dataframes

    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        format_row_based_diff(expected_df, actual_df)
        output = fake_out.getvalue()

    assert output == snapshot


class TestFormatRowBasedDiff:
    def test_with_value_diffs(self, sample_dataframes, snapshot):
        """Test formatting DataFrame differences with value differences."""
        expected_df, actual_df = sample_dataframes

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            format_dataframe_diff(expected_df, actual_df)
            output = fake_out.getvalue()

        assert output == snapshot

    def test_with_column_mismatch(self, column_mismatch_dataframes, snapshot):
        """Test formatting DataFrame differences with column mismatches."""
        expected_df, actual_df = column_mismatch_dataframes

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            format_dataframe_diff(expected_df, actual_df)
            output = fake_out.getvalue()

        assert output == snapshot

    def test_with_row_count_mismatch(self, row_count_mismatch_dataframes, snapshot):
        """Test formatting DataFrame differences with row count mismatches."""
        expected_df, actual_df = row_count_mismatch_dataframes

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            format_dataframe_diff(expected_df, actual_df)
            output = fake_out.getvalue()

        assert output == snapshot


class TestFormatTestSummary:
    def test_summary_all_passed(self, snapshot):
        """Test formatting a test summary with all tests passed."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            format_test_summary(5, 5)
            output = fake_out.getvalue()

        assert output == snapshot

    def test_summary_some_failed(self, snapshot):
        """Test formatting a test summary with some tests failed."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            format_test_summary(5, 3)
            output = fake_out.getvalue()

        assert output == snapshot
