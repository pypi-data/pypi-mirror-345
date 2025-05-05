import json
import os
import inspect
from typing import Callable, Optional
from decimal import Decimal

from . import PySparkFixtures

import pytest

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


def compare_lists(result: list, expected: list) -> None:
    result_len = len(result)
    expected_len = len(expected)
    assert (
        result_len == expected_len
    ), f"Length mismatch: len(result)={result_len=} != len(expected)={expected_len=}"
    for result_row, expected_row in zip(result, expected):
        compare_dicts(result_row, expected_row)


def compare_dicts(result_row: dict, expected_row: dict) -> None:
    for field, result_value in result_row.items():
        try:
            expected_value = expected_row[field]
        except KeyError as ex:
            raise ValueError(
                f"The column '{field}' doesn't exist in the expected result row {expected_row}"
            ) from ex

        if isinstance(result_value, (float, Decimal)) and isinstance(
            expected_value, (float, Decimal)
        ):
            assert result_value == pytest.approx(expected_value), (
                f"Field {field} mismatch: result_value={result_value} != expected_value={expected_value} "
                f"Row: {result_row} vs {expected_row}"
            )
        else:
            assert result_value == expected_value, (
                f"Field {field} mismatch: result_value='{result_value}' ({type(result_value)}) and expected_value='{expected_value}' ({type(expected_value)}) "
                f"Row {result_row} vs {expected_row}"
            )


def compare_dfs(result_df: DataFrame, expected_df: DataFrame) -> None:
    result = result_df.orderBy(*result_df.columns).collect()
    expected = expected_df.orderBy(*expected_df.columns).collect()

    result_len = len(result)
    expected_len = len(expected)
    assert (
        result_len == expected_len
    ), f"Rows count mismatch:, len(result_df)={result_len=} != len(expected_df){expected_len=}"

    for result_row, expected_row in zip(result, expected):
        compare_dicts(
            result_row.asDict(),
            expected_row.asDict(),
        )


def compare_dfs_schemas(
    result_schema: StructType,
    expected_schema: StructType,
    check_nullability: bool = False,
) -> None:
    result_columns = [
        (f.name, f.dataType.simpleString(), f.nullable if check_nullability else None)
        for f in result_schema.fields
    ]
    expected_columns = [
        (f.name, f.dataType.simpleString(), f.nullable if check_nullability else None)
        for f in expected_schema.fields
    ]
    assert (
        result_columns == expected_columns
    ), f"Schemas mismatch found: {result_schema} != {expected_schema}"


def get_spark_session(
    warehouse_dir: Optional[str] = None,
    extra_configs: Optional[dict[str, str]] = None,
) -> SparkSession:
    if not warehouse_dir:
        caller_file = inspect.stack()[1].filename
        caller_dir = os.path.dirname(caller_file)
        warehouse_dir = os.path.join(caller_dir, "pytest-data")

    builder = (
        SparkSession.builder.appName("unit-tests")
        .config("spark.driver.extraJavaOptions", "-Duser.timezone=GMT")
        .config("spark.executor.extraJavaOptions", "-Duser.timezone=GMT")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", 1)
        .config("spark.sql.warehouse.dir", warehouse_dir)
    )

    if extra_configs is not None:
        for key, value in extra_configs.items():
            builder = builder.config(key, value)

    return builder.master("local[1]").getOrCreate()


def get_table_schema(db_name: str, table_name: str, base_path: str) -> StructType:
    schema_path = f"{base_path}/{db_name}/{table_name}.json"
    with open(schema_path) as f:
        schema = json.load(f)

    for field in schema["fields"]:
        field["metadata"] = field.get("metadata", {})
        field["nullable"] = field.get("nullable", True)

    return StructType.fromJson(schema)


def generic_empty_input_tables_test(
    spark_session: SparkSession,
    input_tables: list[tuple],
    output_tables: list[tuple],
    run_spark_job: Callable,
    schemas_fetcher: Callable,
    no_assert: bool = False,
) -> None:
    """
    Generic test that can be used to test any spark job

    It populates all the used tables empty and runs the spark job

    By default expects the output tables to be empty
    """
    dbs_used = set(t[0] for t in input_tables + output_tables)

    for db_name in dbs_used:
        spark_session.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    # Creating empty tables
    for db_name, table_name in input_tables:
        df = spark_session.createDataFrame(
            [],
            schemas_fetcher(f"{db_name}.{table_name}"),
        )
        df.write.mode("overwrite").saveAsTable(f"{db_name}.{table_name}")

    run_spark_job()

    if no_assert:
        return

    for db_name, table_name in output_tables:
        assert spark_session.table(f"{db_name}.{table_name}").count() == 0


def generic_populated_input_tables_test(
    spark_session: SparkSession,
    input_tables: list[tuple],
    output_tables: list[tuple],
    run_spark_job: Callable,
    fixtures: PySparkFixtures,
    no_assert: bool = False,
) -> None:
    """
    Generic test that can be used to test any spark job

    It populates all the used tables using the fixtures data and runs the spark job

    Finally it make sures the result tables are identical to the expected fixtures
    """
    tables_to_create: list[tuple[str, str]] = [
        (t[0], t[1]) for t in input_tables.copy()
    ]

    tables_to_create.extend((t[0], f"{t[1]}__expected") for t in output_tables)

    dbs_used = set(t[0] for t in tables_to_create)
    for db_name in dbs_used:
        spark_session.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}")

    for db_name, table_name in tables_to_create:
        full_table_name = f"{db_name}.{table_name}"
        test_df = fixtures.get_dataframe(full_table_name)
        test_df.write.mode("overwrite").saveAsTable(full_table_name)

    run_spark_job()

    if no_assert:
        return

    for db_name, table_name in output_tables:
        full_table_name = f"{db_name}.{table_name}"
        result_df = spark_session.table(full_table_name)
        expected_result_table_name = f"{full_table_name}__expected"
        expected_result_df = spark_session.table(expected_result_table_name)

        compare_dfs(result_df, expected_result_df)
