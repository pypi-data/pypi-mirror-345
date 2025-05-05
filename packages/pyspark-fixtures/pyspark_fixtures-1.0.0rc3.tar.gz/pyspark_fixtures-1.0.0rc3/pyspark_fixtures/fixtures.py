import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    BooleanType,
    ByteType,
    DataType,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    StructType,
    TimestampType,
)


class SchemaNotFoundError(Exception):
    """
    Exception raised when a fixtures table doesn't have an schema defined inline
    and there is no schema fetcher callback available, so there is no way to get the schema
    """

    pass


class PySparkFixtures:
    def __init__(
        self,
        fixtures_file: str,
        spark: SparkSession,
        schemas_fetcher: Optional[Callable] = None,
    ) -> None:
        """
        Initializes a PySparkFixtures object

        Args:
            fixtures_file (str): Full path of the file with the data fixtures
            spark (SparkSession): A Spark session, you can use helper.get_spark_session()
            schemas_fetcher (Optional[Callable]): Callback function that returns an Spark schema for a given table name
        """

        self._spark = spark
        self._tables, self._schemas = self._extract_file(fixtures_file, schemas_fetcher)

    def get_table(self, name: str) -> list[dict]:
        """
        Gets the table data as a list of dictionaries
        """
        try:
            table = self._tables[name]
        except KeyError as ex:
            raise ValueError(f"Table not found '{name}'") from ex
        schema = self.get_schema(name)
        try:
            return self._convert_table(table, schema)
        except Exception as ex:
            raise ValueError(f"Error converting table '{name}'") from ex

    def get_schema(self, name: str) -> StructType:
        """
        Gets the table Spark schema
        """
        return self._schemas[name]

    def get_dataframe(self, name: str) -> DataFrame:
        """
        Gets a table Spark DataFrame
        """
        typed_table = self.get_table(name)
        schema = self.get_schema(name)
        return self._spark.createDataFrame(typed_table, schema)  # type: ignore

    @staticmethod
    def _clean_schema_id(schema_id: str) -> str:
        """
        A schema id can be part of a markdown link so it has to be extracted
        """
        clean_schema_id = schema_id.strip()
        potential_md_links = re.search(r"\[([^\]]+)\]\([^\)]+\)", clean_schema_id)
        if potential_md_links:
            clean_schema_id = potential_md_links.group(1).strip()
        return clean_schema_id

    @classmethod
    def _extract_schema_id(cls, lines: list[str]) -> Optional[str]:
        schema_id = None
        for li in lines:
            # If we find a | data has started then there is no schema id
            if re.match(r"^\|", li):
                break
            if re.match(r"^\s*Schema\s*:", li):
                raw_schema_id = li.split(":")[1]
                schema_id = cls._clean_schema_id(raw_schema_id)
                break
        return schema_id

    @classmethod
    def _extract_data_lines(cls, lines: list[str]) -> list[list[str]]:
        return [
            [
                value.replace(r"\|", "|")  # Removing escape character \
                # Spliting by | considering escape char \ and ignoring first and last empty values
                for value in re.split(r"\s*(?<!\\)\|\s*", line.strip())[1:-1]
            ]
            for line in lines
            if re.match(r"^\|", line)  # Lines not starting | are not rows
        ]

    @classmethod
    def _is_markdown_format(cls, data: list[list[str]]) -> bool:
        """
        When is a markdown table the second line has | --- | --- |
        """
        second_line = data[0]
        is_markdown_format = all(
            re.match(r"^\s*[:-]+\s*$", value) for value in second_line
        )
        return is_markdown_format

    @classmethod
    def _extract_table(
        cls, lines: list[str]
    ) -> tuple[list[dict], Optional[dict], Optional[str]]:
        """
        returns:
            - table
            - schema
            - schema id if it was defined
        """
        # Extract the schema id if it's defined
        schema_id = cls._extract_schema_id(lines)

        data = cls._extract_data_lines(lines)

        header = data.pop(0)  # The first line is for the columns

        columns_names, data_types = cls._extract_col_names_and_types(header)

        if cls._is_markdown_format(data):
            # If it's in markdown format we have to ignore the line after the header
            # because it's just a markdown format line | --- | --- | --- |
            data.pop(0)

        result_schema = None
        if not schema_id:
            # If no schema id is defined and no data types were extracted from the header
            # the second line of data has the schema definition
            if not data_types:
                data_types = data.pop(0)

            # Removing backticks and stars from the data types values
            clean_data_types = map(
                lambda col_val: col_val.replace("`", "").replace("*", ""), data_types
            )

            result_schema = dict(zip(columns_names, clean_data_types))

        result_data = [dict(zip(columns_names, row)) for row in data]

        return (
            result_data,
            result_schema,
            schema_id,
        )

    @classmethod
    def _extract_col_names_and_types(
        self, header: list[str]
    ) -> tuple[list[str], list[str]]:
        col_names = []
        data_types = []

        for val in header:
            val_split = val.split("[")
            name = val_split[0].strip()
            col_names.append(name)
            if len(val_split) > 1:
                col_type = val_split[1].replace("]", "").strip()
                data_types.append(col_type)

        if data_types and len(col_names) != len(data_types):
            raise ValueError(f"Some columns are missing the data types: {header}")

        return (col_names, data_types)

    @classmethod
    def _extract_file(
        cls, fixtures_file: str, schemas_fetcher: Optional[Callable] = None
    ) -> tuple[dict, dict]:
        with open(fixtures_file) as f:
            file_content = f.read()
        tables = {}
        schemas = {}
        table_texts = re.split(
            r"^\s*#*\s*Table:\s*", file_content.strip(), flags=re.MULTILINE
        )
        # Skipping anything before the first line with Table:
        table_texts.pop(0)
        for table_raw in table_texts:
            lines = table_raw.split("\n")
            table_name = lines[0].strip()
            # Removing line with the table name
            lines.pop(0)
            extracted_table, extracted_schema, schema_id = cls._extract_table(lines)
            if schema_id and not schemas_fetcher:
                raise SchemaNotFoundError(
                    f"Table id '{table_name}' has the schema id: '{schema_id}' but not an schema fetcher"
                )
            tables[table_name] = extracted_table
            if schema_id and schemas_fetcher:
                schemas[table_name] = schemas_fetcher(schema_id)
            elif extracted_schema is not None:
                schemas[table_name] = cls._convert_to_struct_type(extracted_schema)
        return tables, schemas

    @classmethod
    def _convert_to_struct_type(cls, dict_schema: dict) -> StructType:
        fields = []

        for col_name, col_type in dict_schema.items():
            col_type = col_type.lower().strip()
            clean_col_type, num_replacements = re.subn(
                r"\s+not\s+null\s*", "", col_type
            )
            nullable = num_replacements == 0
            fields.append(
                {
                    "name": col_name,
                    "type": clean_col_type,
                    "metadata": {},
                    "nullable": nullable,
                }
            )

        return StructType.fromJson(
            {
                "fields": fields,
                "type": "struct",
            }
        )

    def _get_typed_val(self, col_type: Optional[DataType], col_value: Any) -> Any:
        if col_value == "<NULL>":
            return None

        if isinstance(col_type, DecimalType):
            return Decimal(col_value)

        if isinstance(col_type, (FloatType, DoubleType)):
            return float(col_value)

        if isinstance(col_type, (ShortType, ByteType, IntegerType, LongType)):
            return int(col_value)

        if isinstance(col_type, DateType):
            return datetime.strptime(col_value, "%Y-%m-%d")

        if isinstance(col_type, TimestampType):
            try:
                return datetime.strptime(col_value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return datetime.strptime(col_value, "%Y-%m-%d %H:%M:%S.%f")

        if isinstance(col_type, BooleanType):
            if col_value == "false":
                return False
            elif col_value == "true":
                return True
            else:
                return None

        return col_value

    def _convert_table(self, table: list[dict], schema: StructType) -> list[dict]:
        result = []
        data_types = {field.name: field.dataType for field in schema}

        for row in table:
            typed_row = {}
            for col_name, col_value in row.items():
                try:
                    col_type = data_types[col_name]
                except KeyError as ex:
                    raise ValueError(
                        f"Column '{col_name}' not found in the schema"
                    ) from ex
                try:
                    typed_val = self._get_typed_val(col_type, col_value)
                except Exception as ex:
                    raise ValueError(
                        f"Error converting field: '{col_name}', '{col_value}', '{col_type}'"
                    ) from ex
                typed_row[col_name] = typed_val
            result.append(typed_row)

        return result
