"""Tests for the sqltest package."""

from sqltesty.runner import run_sql_test, run_sql_tests


def test_run_sql_test_success(tmp_path):
    """Test successful SQL test execution."""
    # Create test directory structure
    sql_file = tmp_path / "query.sql"
    test_dir = tmp_path / "tests" / "sqltest"
    fixture_dir = test_dir / "query"
    fixture_dir.mkdir(parents=True)

    # Create SQL file
    sql_file.write_text("SELECT * FROM test_table WHERE value > 5")

    # Create fixture files
    test_table_csv = fixture_dir / "test_table.csv"
    test_table_csv.write_text("id,value\n1,10\n2,3\n3,7\n")

    output_csv = fixture_dir / "output.csv"
    output_csv.write_text("id,value\n1,10\n3,7\n")

    # Run test
    result = run_sql_test(sql_file, test_dir, verbose=True)

    assert result is True


def test_run_sql_test_failure(tmp_path):
    """Test SQL test with incorrect expected output."""
    # Create test directory structure
    sql_file = tmp_path / "query.sql"
    test_dir = tmp_path / "tests" / "sqltest"
    fixture_dir = test_dir / "query"
    fixture_dir.mkdir(parents=True)

    # Create SQL file
    sql_file.write_text("SELECT * FROM test_table WHERE value > 5")

    # Create fixture files
    test_table_csv = fixture_dir / "test_table.csv"
    test_table_csv.write_text("id,value\n1,10\n2,3\n3,7\n")

    # Incorrect output (missing a row that should be included)
    output_csv = fixture_dir / "output.csv"
    output_csv.write_text("id,value\n1,10\n")

    # Run test
    result = run_sql_test(sql_file, test_dir, verbose=True)

    assert result is False


def test_run_sql_tests(tmp_path):
    """Test running multiple SQL tests."""
    # Create test directory structure
    test_dir = tmp_path / "tests" / "sqltest"
    test_dir.mkdir(parents=True)

    # Create two SQL files
    sql_file1 = tmp_path / "query1.sql"
    sql_file1.write_text("SELECT * FROM test_table WHERE value > 5")

    sql_file2 = tmp_path / "query2.sql"
    sql_file2.write_text("SELECT COUNT(*) as count FROM test_table")

    # Create fixture directories and files
    fixture_dir1 = test_dir / "query1"
    fixture_dir1.mkdir()

    test_table_csv1 = fixture_dir1 / "test_table.csv"
    test_table_csv1.write_text("id,value\n1,10\n2,3\n3,7\n")

    output_csv1 = fixture_dir1 / "output.csv"
    output_csv1.write_text("id,value\n1,10\n3,7\n")

    fixture_dir2 = test_dir / "query2"
    fixture_dir2.mkdir()

    test_table_csv2 = fixture_dir2 / "test_table.csv"
    test_table_csv2.write_text("id,value\n1,10\n2,3\n3,7\n")

    output_csv2 = fixture_dir2 / "output.csv"
    output_csv2.write_text("count\n3\n")

    # Run tests
    result = run_sql_tests(test_dir, verbose=True)

    assert result is True
