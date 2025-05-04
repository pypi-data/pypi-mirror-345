from typing import Dict, Any, List
from pyspark.sql import DataFrame


def resolve_function_value(func_config: Dict, df: DataFrame, worksheet: Any, header: List[str] = None):
    """
    Resolve a function reference to its actual value, with type conversion.

    Args:
        func_config: Dict with function, source, and column keys
        df: Source DataFrame
        worksheet: Source worksheet
        header: List of column names for the sheet (if available)

    Returns:
        The resolved value
    """
    from .utils import convert_value

    func_name = func_config["function"]
    source = func_config["source"]  # "dataframe" or "sheet"
    column = func_config["column"]

    # Function registry for dataframe operations
    df_functions = {
        "MIN": lambda df, col: df.agg({col: "min"}).collect()[0][0],
        "MAX": lambda df, col: df.agg({col: "max"}).collect()[0][0],
        "FIRST": lambda df, col: df.select(col).first()[0] if df.count() > 0 else None,
        "LAST": lambda df, col: df.orderBy(col.desc()).select(col).first()[0] if df.count() > 0 else None,
        "COUNT": lambda df, col: df.count()
    }

    # Function registry for sheet operations
    sheet_functions = {
        "MIN": lambda ws, col, hdr: min([r[hdr.index(col)] for r in ws.get_all_values()[1:] if r[hdr.index(col)]]),
        "MAX": lambda ws, col, hdr: max([r[hdr.index(col)] for r in ws.get_all_values()[1:] if r[hdr.index(col)]]),
        "FIRST": lambda ws, col, hdr: ws.get_all_values()[1][hdr.index(col)] if len(ws.get_all_values()) > 1 else None,
        "LAST": lambda ws, col, hdr: ws.get_all_values()[-1][hdr.index(col)] if len(ws.get_all_values()) > 1 else None,
        "COUNT": lambda ws, col, hdr: len(ws.get_all_values()) - 1  # Subtract header row
    }

    if func_name not in df_functions and source == "dataframe":
        raise ValueError(f"Unknown dataframe function: {func_name}")
    if func_name not in sheet_functions and source == "sheet":
        raise ValueError(f"Unknown sheet function: {func_name}")

    try:
        if source == "dataframe":
            # Get column data type for conversion
            col_idx = df.columns.index(column)
            dtype = df.schema[col_idx].dataType.typeName()

            # Get raw value from DataFrame
            raw_value = df_functions[func_name](df, column)

            # Convert value using the existing GPP conversion logic
            return convert_value(raw_value, dtype)

        elif source == "sheet":
            if not header:
                header = worksheet.get_all_values()[0] if worksheet.get_all_values() else []

            if column not in header:
                raise ValueError(f"Column '{column}' not found in sheet header: {header}")

            # Get value from sheet
            value = sheet_functions[func_name](worksheet, column, header)

            # For sheet values, we return as-is (already string format in sheets)
            return value
        else:
            raise ValueError(f"Unknown source: {source}")
    except Exception as e:
        raise ValueError(f"Error resolving function {func_name} on {source}.{column}: {str(e)}")