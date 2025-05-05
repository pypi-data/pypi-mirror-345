import logging
import os
import shutil
from datetime import datetime

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    IntegerType,
    DateType,
    DoubleType,
    StringType,
    StructField,
    StructType,
)

from pyspark_fixtures import (
    PySparkFixtures,
    SchemaNotFoundError,
)

from pyspark_fixtures.helpers import (
    compare_lists,
    compare_dfs_schemas,
    get_spark_session,
    get_table_schema,
)

logger = logging.getLogger()


class TestPySparkFixtures:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_FIXTURES_PATH = f"{CURRENT_DIR}/pyspark_fixtures.tests.md"
    PYSPARK_DATA_DIR = os.path.join(CURRENT_DIR, "pyspark-data")

    _spark: SparkSession

    @classmethod
    def setup_class(cls) -> None:
        cls.teardown_class()

        cls._spark = get_spark_session(cls.PYSPARK_DATA_DIR)

    @classmethod
    def teardown_class(cls) -> None:
        shutil.rmtree(cls.PYSPARK_DATA_DIR, ignore_errors=True)

    @classmethod
    def schemas_fetcher(cls, table_name: str) -> StructType:
        db_name, table_name, *_ = table_name.split(".")
        return get_table_schema(
            db_name, table_name, base_path=f"{cls.CURRENT_DIR}/schemas"
        )

    def test__test_fixtures_class(self) -> None:
        fixtures = PySparkFixtures(
            self.FILE_FIXTURES_PATH, self._spark, self.schemas_fetcher
        )
        expected_tables = {
            "table_1": [
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 11, 1, 0, 0),
                    "some_value": 2.0,
                    "some_other_value": 20.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 9, 1, 0, 0),
                    "some_value": 0.0,
                    "some_other_value": 100.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 8, 1, 0, 0),
                    "some_value": 4.0,
                    "some_other_value": 70.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 7, 1, 0, 0),
                    "some_value": 5.0,
                    "some_other_value": 53.5,
                },
                {
                    "col1": "cat2",
                    "col2": "yyyyyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 5, 1, 0, 0),
                    "some_value": 7.55,
                    "some_other_value": 353.0,
                },
                {
                    "col1": "cat2",
                    "col2": "yyyyyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 4, 1, 0, 0),
                    "some_value": 41.2,
                    "some_other_value": 1.3,
                },
                {
                    "col1": "cat2",
                    "col2": "yyyyyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 3, 1, 0, 0),
                    "some_value": 1100.68,
                    "some_other_value": 8001.0,
                },
            ],
            "table_2": [
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 11, 1, 0, 0),
                    "some_value": 4.0,
                    "some_other_value": 40.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 9, 1, 0, 0),
                    "some_value": 20.0,
                    "some_other_value": 300.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxxxxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 8, 1, 0, 0),
                    "some_value": 6.0,
                    "some_other_value": 90.0,
                },
                {
                    "col1": "cat1",
                    "col2": "xxx|xxx33",
                    "col3": "0002",
                    "col4": "A1",
                    "some_date": datetime(2025, 7, 1, 0, 0),
                    "some_value": 7.0,
                    "some_other_value": 73.5,
                },
                {
                    "col1": "cat2",
                    "col2": "yyy|yyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 5, 1, 0, 0),
                    "some_value": 27.55,
                    "some_other_value": 553.0,
                },
                {
                    "col1": "cat2",
                    "col2": "yyy|yyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 4, 1, 0, 0),
                    "some_value": 61.2,
                    "some_other_value": 201.3,
                },
                {
                    "col1": "cat2",
                    "col2": "yyy|yyyjp",
                    "col3": "0004",
                    "col4": "B2",
                    "some_date": datetime(2025, 3, 1, 0, 0),
                    "some_value": 2200.68,
                    "some_other_value": 10001.0,
                },
            ],
        }

        assert expected_tables["table_1"] == fixtures.get_table("table_1")

        assert expected_tables["table_1"] == fixtures.get_table("table_md_format")

        assert expected_tables["table_2"] == fixtures.get_table("table_2")

        result_df = fixtures.get_dataframe("table_2")

        expected_schema = StructType(
            [
                StructField("col1", StringType(), True),
                StructField("col2", StringType(), True),
                StructField("col3", StringType(), True),
                StructField("col4", StringType(), True),
                StructField("some_date", DateType(), True),
                StructField("some_value", DoubleType(), True),
                StructField("some_other_value", DoubleType(), False),
            ]
        )
        compare_dfs_schemas(result_df.schema, expected_schema, check_nullability=True)

    @pytest.mark.parametrize(
        "raw_schema_id, expected_result",
        [
            (
                "  some_db.some_table   ",
                "some_db.some_table",
            ),
            (
                r"[test_db.test_table](../schemas/test_db/test_table.json)",
                "test_db.test_table",
            ),
            (
                r"[  other_schema.other_table   ](../schemas/test_db/test_table.json)",
                "other_schema.other_table",
            ),
        ],
    )
    def test__test_fixtures_class__clean_raw_schema_id(
        self, raw_schema_id, expected_result
    ) -> None:
        assert PySparkFixtures._clean_schema_id(raw_schema_id) == expected_result

    def test__test_fixtures_class_no_schema(self) -> None:
        with pytest.raises(SchemaNotFoundError) as ex:
            PySparkFixtures(self.FILE_FIXTURES_PATH, self._spark)
        assert (
            str(ex.value)
            == "Table id 'table_schema_fetcher_1' has the schema id: 'test_db.test_table' but not an schema fetcher"
        )

    def test__test_fixtures_class_schema_fetcher(self) -> None:
        fixtures = PySparkFixtures(
            self.FILE_FIXTURES_PATH, self._spark, self.schemas_fetcher
        )
        result_df1 = fixtures.get_dataframe("table_schema_fetcher_1")

        expected_output = [
            {"test_col1": "aaa", "test_col2": 1},
            {"test_col1": "bbb", "test_col2": 2},
            {"test_col1": "ccc", "test_col2": 3},
        ]
        compare_lists(
            [r.asDict() for r in sorted(result_df1.collect())], expected_output
        )
        result_df2 = fixtures.get_dataframe("table_schema_fetcher_2")
        compare_lists(
            [r.asDict() for r in sorted(result_df2.collect())], expected_output
        )

    def test_compare_dfs_schemas_matching_without_nullability(self) -> None:
        schema1 = StructType(
            [
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), False),
            ]
        )
        schema2 = StructType(
            [
                StructField("name", StringType(), False),  # nullability ignored
                StructField("age", IntegerType(), True),
            ]
        )
        compare_dfs_schemas(schema1, schema2, check_nullability=False)

        def test_compare_dfs_schemas_matching_with_nullability(self) -> None:
            schema1 = StructType(
                [
                    StructField("name", StringType(), True),
                    StructField("age", IntegerType(), False),
                ]
            )
            schema2 = StructType(
                [
                    StructField("name", StringType(), True),
                    StructField("age", IntegerType(), False),
                ]
            )
            compare_dfs_schemas(schema1, schema2, check_nullability=True)

        def test_compare_dfs_schemas_mismatched_column_name(self) -> None:
            schema1 = StructType(
                [
                    StructField("name", StringType(), True),
                ]
            )
            schema2 = StructType(
                [
                    StructField("full_name", StringType(), True),
                ]
            )
            with pytest.raises(AssertionError, match="Schemas mismatch found"):
                compare_dfs_schemas(schema1, schema2)

        def test_compare_dfs_schemas_mismatched_data_type(self) -> None:
            schema1 = StructType(
                [
                    StructField("age", IntegerType(), True),
                ]
            )
            schema2 = StructType(
                [
                    StructField("age", StringType(), True),
                ]
            )
            with pytest.raises(AssertionError, match="Schemas mismatch found"):
                compare_dfs_schemas(schema1, schema2)

        def test_compare_dfs_schemas_mismatched_nullability_with_check(self) -> None:
            schema1 = StructType(
                [
                    StructField("age", IntegerType(), True),
                ]
            )
            schema2 = StructType(
                [
                    StructField("age", IntegerType(), False),
                ]
            )
            with pytest.raises(AssertionError, match="Schemas mismatch found"):
                compare_dfs_schemas(schema1, schema2, check_nullability=True)

        def test_compare_dfs_schemas_ignore_nullability_difference(self) -> None:
            schema1 = StructType(
                [
                    StructField("age", IntegerType(), True),
                ]
            )
            schema2 = StructType(
                [
                    StructField("age", IntegerType(), False),
                ]
            )
            compare_dfs_schemas(schema1, schema2, check_nullability=False)

    def test_compare_dfs_schemas_column_order_matters(self) -> None:
        schema1 = StructType(
            [
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True),
            ]
        )
        schema2 = StructType(
            [
                StructField("age", IntegerType(), True),
                StructField("name", StringType(), True),
            ]
        )
        with pytest.raises(AssertionError):
            compare_dfs_schemas(schema1, schema2)
