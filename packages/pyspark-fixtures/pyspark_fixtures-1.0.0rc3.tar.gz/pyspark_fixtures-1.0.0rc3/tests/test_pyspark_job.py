import os
import shutil

from typing import Final
from datetime import datetime

from pyspark_fixtures import PySparkFixtures

from pyspark_fixtures.helpers import (
    compare_dfs,
    compare_dfs_schemas,
    get_spark_session,
    get_table_schema,
    generic_empty_input_tables_test,
    generic_populated_input_tables_test,
)

from tests.pyspark_job import MyPySparkJob

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType


class TestPysparkJob:
    CURRENT_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
    PYSPARK_DATA_DIR: Final[str] = f"{CURRENT_DIR}/pytest-data"

    _spark: SparkSession

    @classmethod
    def setup_class(cls) -> None:
        cls.teardown_class()

        spark = get_spark_session(cls.PYSPARK_DATA_DIR)

        spark.sql("CREATE DATABASE IF NOT EXISTS input_db")
        spark.sql("CREATE DATABASE IF NOT EXISTS my_db")

        cls._spark = spark

        # Freezing time so the unit tests pass every day
        MyPySparkJob.set_current_datetime(datetime(2025, 1, 1, 9, 0, 0))

    @classmethod
    def teardown_class(cls) -> None:
        shutil.rmtree(cls.PYSPARK_DATA_DIR, ignore_errors=True)

    def test__transformation(self) -> None:
        """Test only for the transformation method"""
        spark_job = MyPySparkJob(self._spark)

        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/pyspark_job.tests.md", self._spark
        )

        table1_df = fixtures.get_dataframe("input_db.table1")
        table2_df = fixtures.get_dataframe("input_db.table2")

        expected_df = fixtures.get_dataframe("my_db.my_table__expected")

        result_df = spark_job._transformation(table1_df, table2_df)

        compare_dfs(result_df, expected_df)

        compare_dfs_schemas(result_df.schema, expected_df.schema)

    def test__transformation_with_sql(self) -> None:
        """Test only for the transformation method"""
        spark_job = MyPySparkJob(self._spark)

        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/pyspark_job.tests.md", self._spark
        )

        table1_df = fixtures.get_dataframe("input_db.table1")
        table2_df = fixtures.get_dataframe("input_db.table2")

        expected_df = fixtures.get_dataframe("my_db.my_table__expected")

        result_df = spark_job._transformation_with_sql(table1_df, table2_df)

        compare_dfs(result_df, expected_df)

        compare_dfs_schemas(result_df.schema, expected_df.schema)

    def test_run(self) -> None:
        """
        Testing the whole spark job populating the tables locally
        """

        spark_job = MyPySparkJob(self._spark)

        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/pyspark_job.tests.md", self._spark
        )

        table1_df = fixtures.get_dataframe("input_db.table1")
        table1_df.write.mode("overwrite").saveAsTable("input_db.table1")

        table2_df = fixtures.get_dataframe("input_db.table2")
        table2_df.write.mode("overwrite").saveAsTable("input_db.table2")

        spark_job.run()

        result_df = self._spark.table("my_db.my_table")

        expected_df = fixtures.get_dataframe("my_db.my_table__expected")

        compare_dfs(result_df, expected_df)

    def test_populated_input_tables(self) -> None:
        """
        Testing the whole spark job populating the tables locally
        It's the same as test_run but using the generic test instead of
        implementing it manually
        """
        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/pyspark_job.tests.md",
            self._spark,
        )
        generic_populated_input_tables_test(
            self._spark,
            MyPySparkJob.INPUT_TABLES,
            MyPySparkJob.OUTPUT_TABLES,
            lambda: MyPySparkJob(self._spark).run(),
            fixtures,
        )

    @classmethod
    def schemas_fetcher(cls, table_name: str) -> StructType:
        db_name, table_name, *_ = table_name.split(".")
        base_path = f"{cls.CURRENT_DIR}/schemas"
        return get_table_schema(db_name, table_name, base_path)

    def test_empty_input_tables(self) -> None:
        """
        Testing the whole spark job populating empty tables locally
        """
        generic_empty_input_tables_test(
            self._spark,
            MyPySparkJob.INPUT_TABLES,
            MyPySparkJob.OUTPUT_TABLES,
            lambda: MyPySparkJob(self._spark).run(),
            schemas_fetcher=self.schemas_fetcher,
        )

    def test_populated_input_tables_with_schemas_fetcher(self) -> None:
        """
        Testing the whole spark job populating the tables locally
        """
        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/pyspark_job_schemas_fetcher.tests.md",
            self._spark,
            self.schemas_fetcher,
        )
        generic_populated_input_tables_test(
            self._spark,
            MyPySparkJob.INPUT_TABLES,
            MyPySparkJob.OUTPUT_TABLES,
            lambda: MyPySparkJob(self._spark).run(),
            fixtures,
        )
