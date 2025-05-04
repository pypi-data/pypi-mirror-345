# gspreadplusplus

A Python library that enhances Google Sheets operations with additional functionality and improved data type handling.

## Features

- Transfer Spark DataFrames to Google Sheets with proper type conversion
- Append data to existing sheets while maintaining structure
- **NEW: Selectively update portions of sheets with advanced operations (delete specific rows, sort data)**
- Intelligent handling of various data types (numbers, dates, timestamps, etc.)
- **NEW: Dynamic value references between DataFrame and sheet data**
- Preserve or update sheet headers
- Selective column clearing options
- Automatic date formatting
- Sheet dimension management
- Configuration management with key-value storage

## Installation

```bash
pip install gspreadplusplus
```

## Requirements

- Python 3.7+
- gspread
- pyspark
- google-auth

## Usage

### Basic DataFrame Export

```python
from gpp import GPP
from pyspark.sql import SparkSession

# Initialize Spark and create a DataFrame
spark = SparkSession.builder.appName("example").getOrCreate()
df = spark.createDataFrame([
    ("2024-01-01", 100, "Complete"),
    ("2024-01-02", 150, "Pending")
], ["date", "amount", "status"])

# Your Google Sheets credentials
creds_json = {
    "type": "service_account",
    # ... rest of your service account credentials
}

# Export DataFrame to Google Sheets
GPP.df_to_sheets(
    df=df,
    spreadsheet_id="your_spreadsheet_id",
    sheet_name="Sheet1",
    creds_json=creds_json
)
```

### Append Data to Existing Sheet

```python
# Append data to existing sheet
GPP.df_append_to_sheets(
    df=df,
    spreadsheet_id="your_spreadsheet_id",
    sheet_name="Sheet1",
    creds_json=creds_json,
    keep_header=True,     # Keep existing header
    create_sheet=True     # Create sheet if it doesn't exist
)
```

### NEW! Partially Update Sheet with Selective Operations

The new `df_overlap_to_sheets` method allows you to perform selective operations on the sheet before appending new data. This is perfect for scenarios like updating time series data where you want to keep some historical data while replacing more recent records.

```python
# Define operations to perform on the sheet before appending
update_config = {
    "operations": [
        # Sort the data by date column
        {"type": "sort", "column": "date", "direction": "asc"},
        
        # Delete rows where date is greater than or equal to Feb 1, 2025
        {"type": "delete_from", "column": "date", "value": "2025-02-01", "inclusive": True}
    ]
}

# Update sheet with selective deletion and then append new data
GPP.df_overlap_to_sheets(
    df=df,
    spreadsheet_id="your_spreadsheet_id",
    sheet_name="Sheet1",
    creds_json=creds_json,
    update_config=update_config,
    keep_header=True,
    create_sheet=True
)
```

### Using Dynamic Function References

You can reference values from your DataFrame or the existing sheet data dynamically:

```python
# Delete rows with timestamps >= the minimum date in your DataFrame
update_config = {
    "operations": [
        {"type": "delete_from", 
         "column": "date", 
         "value": {"function": "MIN", "source": "dataframe", "column": "date"},
         "inclusive": True}
    ]
}

# Or reference values from the sheet itself
update_config = {
    "operations": [
        {"type": "delete_where", 
         "column": "amount", 
         "value": {"function": "MAX", "source": "sheet", "column": "amount"},
         "operator": "eq"}
    ]
}
```

### Configuration Management

The library provides functionality to store and update configuration values in a Google Sheet. By default, it uses a sheet named "CONFIG" with keys in column A and values in column B.

```python
# Store or update a configuration value
result = GPP.set_config(
    spreadsheet_id="your_spreadsheet_id",
    key="api_endpoint",
    value="https://api.example.com",
    creds_json=creds_json,
    sheet_name="CONFIG"  # Optional, defaults to "CONFIG"
)

if result == 0:
    print("Configuration updated successfully")
else:
    print("Error updating configuration")
```

## Method Reference

### df_to_sheets
Exports a Spark DataFrame to Google Sheets, optionally preserving existing headers.

Parameters:
- `df`: Spark DataFrame containing the data to transfer
- `spreadsheet_id`: The ID of the Google Spreadsheet
- `sheet_name`: Name of the worksheet to update
- `creds_json`: Dictionary containing Google service account credentials
- `keep_header`: If True, preserve the first row of the sheet (default: False)
- `erase_whole`: If True, clear all columns and rows (default: True)
- `create_sheet`: If True, create the sheet if it doesn't exist (default: True)

### df_append_to_sheets
Appends data from a Spark DataFrame to an existing Google Sheet.

Parameters:
- `df`: Spark DataFrame containing the data to append
- `spreadsheet_id`: The ID of the Google Spreadsheet
- `sheet_name`: Name of the worksheet to update
- `creds_json`: Dictionary containing Google service account credentials
- `keep_header`: If True, preserve existing header (default: False)
- `create_sheet`: If True, create the sheet if it doesn't exist (default: True)

### NEW! df_overlap_to_sheets
Updates sheet with selective deletion or modification based on configuration, then appends new data.

Parameters:
- `df`: Spark DataFrame containing the data to append
- `spreadsheet_id`: The ID of the Google Spreadsheet
- `sheet_name`: Name of the worksheet to update
- `creds_json`: Dictionary containing Google service account credentials
- `update_config`: Configuration dictionary with operations to perform
- `keep_header`: If True, preserve existing header (default: True)
- `create_sheet`: If True, create the sheet if it doesn't exist (default: True)

#### Supported Operations

The `update_config` dictionary supports these operations:

1. **Sort**
   ```python
   {"type": "sort", "column": "date", "direction": "asc"}
   ```

2. **Delete From**
   ```python
   {"type": "delete_from", "column": "date", "value": "2025-02-01", "inclusive": True}
   ```

3. **Delete Range**
   ```python
   {"type": "delete_range", "column": "amount", "start_value": 100, "end_value": 500, "inclusive": True}
   ```

4. **Delete Where**
   ```python
   {"type": "delete_where", "column": "status", "value": "Pending", "operator": "eq"}
   ```
   Supported operators: "eq", "ne", "gt", "lt", "ge", "le"

5. **Dynamic Function References**
   ```python
   {"value": {"function": "MIN", "source": "dataframe", "column": "date"}}
   ```
   Supported functions: "MIN", "MAX", "FIRST", "LAST", "COUNT"
   Sources: "dataframe", "sheet"

### set_config
Stores or updates configuration values in a designated sheet.

Parameters:
- `spreadsheet_id`: The ID of the Google Spreadsheet
- `key`: The key to store/update
- `value`: The value to set
- `creds_json`: Dictionary containing Google service account credentials
- `sheet_name`: Name of the configuration worksheet (default: "CONFIG")

Returns:
- 0 on success
- 1 on error

## Data Type Support

The library automatically handles conversion of various data types:

- Strings
- Integers (regular, long, bigint)
- Floating point numbers (double, float)
- Decimals
- Dates
- Timestamps
- Booleans

Null values are converted to:
- 0 for numeric types
- Empty string for other types

## Advanced Example: Time Series Data Update

Here's a real-world example of updating a time series dataset where you want to replace data for certain months while keeping historical data intact:

```python
from gpp import GPP
from pyspark.sql import SparkSession

# Create DataFrame with updated data for Feb-May 2025
spark = SparkSession.builder.appName("TimeSeriesUpdate").getOrCreate()
updated_df = spark.createDataFrame([
    ("2025-02-01", 210, "Complete"),
    ("2025-03-01", 325, "Complete"),
    ("2025-04-01", 415, "Complete"),
    ("2025-05-01", 550, "Pending")
], ["date", "amount", "status"])

# Define update configuration
# This will:
# 1. Sort data by date
# 2. Delete existing records for Feb-Apr (keeping January)
# 3. Keep May and beyond if they exist
update_config = {
    "operations": [
        {"type": "sort", "column": "date", "direction": "asc"},
        {"type": "delete_range", 
         "column": "date", 
         "start_value": "2025-02-01",
         "end_value": "2025-04-30",
         "inclusive": True}
    ]
}

# Update the sheet
GPP.df_overlap_to_sheets(
    df=updated_df,
    spreadsheet_id="your_spreadsheet_id",
    sheet_name="MonthlySales",
    creds_json=creds_json,
    update_config=update_config
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.