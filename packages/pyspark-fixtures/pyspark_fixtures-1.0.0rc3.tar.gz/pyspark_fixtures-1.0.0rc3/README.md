# PySpark-fixtures

Simple unit testing for PySpark jobs with readable fixtures for humans and machines, plus helpers to eliminate boilerplate

## Requirements

- Python >= 3.9
- pyspark >= 3.0.0

## Installation

```
pip install pyspark

pip install pyspark-fixtures
```

## Example

This is how readable and simple your unit tests data and documentation could look:

```

You can add here the requirements and details

# Table: my_db.user_actions

| user_id | event_id | event_type | event_date          |
| ------- | -------- | ---------- | ------------------- |
| integer | integer  | string     | timestamp           |
| 445     | 7765     | sign-in    | 2022-05-31 12:00:00 |
| 445     | 3634     | like       | 2022-06-05 12:00:00 |
| 648     | 3124     | like       | 2022-06-18 12:00:00 |
| 648     | 2725     | sign-in    | 2022-06-22 12:00:00 |
| 648     | 8568     | comment    | 2022-07-03 12:00:00 |
| 445     | 4363     | sign-in    | 2022-07-05 12:00:00 |
| 445     | 2425     | like       | 2022-07-06 12:00:00 |
| 445     | 2484     | like       | 2022-07-22 12:00:00 |
| 648     | 1423     | sign-in    | 2022-07-26 12:00:00 |
| 445     | 5235     | comment    | 2022-07-29 12:00:00 |
| 742     | 6458     | sign-in    | 2022-07-03 12:00:00 |
| 742     | 1374     | comment    | 2022-07-19 12:00:00 |


# Table: my_db.output__expected

Input table: my_db.user_actions

| month   | monthly_active_users |
| ------- | -------------------- |
| integer | integer              |
| 6       | 1                    |
| 7       | 8                    |


You can add more clarifications here too
```

This is how easy writing unit tests for a PySpark job is:

```python
class TestUserActionsJob:
    CURRENT_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
    PYSPARK_DATA_DIR: Final[str] = f"{CURRENT_DIR}/pytest-spark-warehouse"

    _spark: SparkSession

    @classmethod
    def setup_class(cls):
        spark = get_spark_session(cls.PYSPARK_DATA_DIR)

        if os.path.exists(cls.PYSPARK_DATA_DIR):
            shutil.rmtree(cls.PYSPARK_DATA_DIR)

        spark.sql("CREATE DATABASE IF NOT EXISTS my_db")

        cls._spark = spark

    def test_user_actions_job_solution(self):
        fixtures = PySparkFixtures(
            f"{self.CURRENT_DIR}/test_data.md",
            self._spark,
        )
        generic_populated_input_tables_test(
            self._spark,
            UserActionsJob.INPUT_TABLES,
            UserActionsJob.OUTPUT_TABLES,
            lambda: UserActionsJob(self._spark).run(),
            fixtures,
        )
```

This exact code works for any spark job, the only different is the input fixtures file name and Spark Job class

PySpark job implementation:


```python
from typing import Final

from pyspark.sql import DataFrame
import pyspark.sql.functions as F


class UserActionsJob:
    OUTPUT_DB_NAME: Final[str] = "my_db"
    INPUT_DB_NAME: Final[str] = "my_db"

    # Used in the unit tests and here for reference
    INPUT_TABLES: Final[list[tuple]] = [
        (INPUT_DB_NAME, "user_actions"),
    ]

    OUTPUT_TABLES: Final[list[tuple]] = [
        (OUTPUT_DB_NAME, "output"),
    ]

    def __init__(self, spark) -> None:
        self._spark = spark

    def _transformation(self, user_actions_df: DataFrame) -> DataFrame:
        clean_df = (
            user_actions_df.withColumn(
                "current_year_month", F.date_format("event_date", "yyyy-MM")
            )
            .withColumn(
                "previous_year_month",
                F.date_format(F.add_months(user_actions_df.event_date, -1), "yyyy-MM"),
            )
            .select("user_id", "current_year_month", "previous_year_month")
        )

        return (
            clean_df.alias("current")
            .join(
                clean_df.alias("previous"),
                (F.col("current.user_id") == F.col("previous.user_id"))
                & (
                    F.col("current.previous_year_month")
                    == F.col("previous.current_year_month")
                ),
            )
            .groupBy(F.month(F.col("current.current_year_month")).alias("month"))
            .agg(F.count(F.lit(1)).alias("monthly_active_users"))
        )

    def run(self) -> None:
        user_actions_df = self._spark.table(f"{self.INPUT_DB_NAME}.user_actions")
        result_df = self._transformation(user_actions_df)

        result_df.write.mode("overwrite").saveAsTable(f"{self.OUTPUT_DB_NAME}.output")
```
