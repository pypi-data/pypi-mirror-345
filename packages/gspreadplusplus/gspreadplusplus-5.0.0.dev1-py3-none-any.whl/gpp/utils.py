from pyspark.sql import DataFrame
from datetime import datetime, time
from typing import List, Any, Dict, Tuple

def convert_value(value: Any, dtype: str) -> Any:
    """
    Convert Spark SQL types to appropriate Python types for Google Sheets.

    Args:
        value: The value to convert
        dtype: The Spark SQL data type name (case-insensitive)

    Returns:
        Converted value suitable for Google Sheets

    Raises:
        ValueError: If dtype is not supported
    """
    dtype = dtype.lower()

    if value is None:
        # Convert nulls to appropriate default values based on type
        return 0 if dtype in ["bigint", "long", "double", "decimal", "float"] else ""

    # Map of data types to conversion functions
    type_handlers = {
        "string": lambda x: str(x),
        "bigint": lambda x: int(x),
        "long": lambda x: int(x),
        "integer": lambda x: int(x),
        "int": lambda x: int(x),
        "tinyint": lambda x: int(x),
        "smallint": lambda x: int(x),
        "short": lambda x: int(x),
        "double": lambda x: round(float(x), 2),
        "float": lambda x: round(float(x), 2),
        "decimal": lambda x: round(float(x), 2),
        "timestamp": lambda x: x.isoformat(),
        "date": lambda x: datetime.combine(x, time.min).isoformat(),
        "boolean": lambda x: bool(x),
        "daytimeinterval": lambda x: str(x)
    }

    if dtype not in type_handlers:
        raise ValueError(f"Unsupported data type: {dtype}")

    return type_handlers[dtype](value)

def prepare_data(df: DataFrame, keep_header: bool) -> Tuple[List[List[Any]], List[int], List[str]]:
    """
    Convert DataFrame to list of lists with proper type conversion.

    Args:
        df: Spark DataFrame to convert
        keep_header: If True, exclude header from converted data

    Returns:
        Tuple containing:
        - List of lists with converted data
        - List of column indices containing dates
        - List of column headers
    """
    # Identify date columns for formatting
    date_columns = [i for i, field in enumerate(df.schema)
                    if field.dataType.typeName().lower() == "date"]

    data = df.collect()
    header = df.columns

    # Include header in converted data only if not keeping existing header
    converted_data = [] if keep_header else [header]

    for row in data:
        converted_row = [
            convert_value(value, df.schema[i].dataType.typeName())
            for i, value in enumerate(row)
        ]
        converted_data.append(converted_row)

    return converted_data, date_columns, header