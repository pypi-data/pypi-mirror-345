from sqltesty.helpers import extract_order_by_columns


class TestExtractOrderByColumns:
    def test_normal_naming(self):
        sql_query = "SELECT * FROM table ORDER BY col1 ASC, col2 DESC, col3"
        assert extract_order_by_columns(sql_query) == ["col1", "col2", "col3"]

        sql_query = "SELECT * FROM table"
        assert extract_order_by_columns(sql_query) == []

        sql_query = "SELECT * FROM table ORDER BY col1, col2 ASC"
        assert extract_order_by_columns(sql_query) == ["col1", "col2"]

        sql_query = "SELECT * FROM table ORDER BY `col1` DESC, [col2], 'col3' ASC"
        assert extract_order_by_columns(sql_query) == ["`col1`", "[col2]", "'col3'"]

    def test_with_aliases(self):
        sql_query = """SELECT col1 AS alias1, col2 AS alias2, col3
                       FROM table
                       ORDER BY col1 ASC, col2 DESC, col3"""
        assert extract_order_by_columns(sql_query) == ["alias1", "alias2", "col3"]

        sql_query = "SELECT col1, col2 AS alias2 FROM table ORDER BY col1, col2 ASC"
        assert extract_order_by_columns(sql_query) == ["col1", "alias2"]

        sql_query = """SELECT `col1` AS `alias1`, [col2] AS [alias2], 'col3' AS 'alias3'
        FROM table
        ORDER BY `col1` DESC, [col2], 'col3' ASC"""
        assert extract_order_by_columns(sql_query) == [
            "`alias1`",
            "[alias2]",
            "'alias3'",
        ]

    def test_table_prefix(self):
        sql_query = """SELECT table1.col1 AS alias1, table2.col2, col3
        FROM table1 JOIN table2 ON table1.id = table2.id
        ORDER BY table1.col1 ASC, table2.col2 DESC, col3"""
        assert extract_order_by_columns(sql_query) == ["alias1", "col2", "col3"]

        sql_query = """SELECT table1.col1, table2.col2 AS alias2
        FROM table1 JOIN table2 ON table1.id = table2.id
        ORDER BY table1.col1, table2.col2 ASC"""
        assert extract_order_by_columns(sql_query) == ["col1", "alias2"]

        sql_query = """SELECT `table1`.`col1` AS `alias1`,
                              [table2].[col2] AS [alias2],
                              'col3' AS 'alias3'
        FROM table1 JOIN table2 ON table1.id = table2.id
        ORDER BY `table1`.`col1` DESC, [table2].[col2], 'col3' ASC"""
        assert extract_order_by_columns(sql_query) == [
            "`alias1`",
            "[alias2]",
            "'alias3'",
        ]
