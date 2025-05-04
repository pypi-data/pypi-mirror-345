from pyspark.sql import DataFrame
from datetime import datetime, time
from gspread import service_account_from_dict
from typing import List, Any, Dict, Tuple
from .utils import convert_value, prepare_data
from .operations import apply_update_operations, process_update_config


class GPP:
    """
    Gspread Plus Plus (GPP) class for enhanced Google Sheets operations.

    This class provides functionality to transfer Spark DataFrames to Google Sheets
    while handling type conversions, date formatting, and sheet management.
    """

    @staticmethod
    def _init_sheets_client(spreadsheet_id: str, sheet_name: str, creds_json: Dict, create_sheet: bool = True) -> Tuple[
        Any, Any]:
        """
        Initialize Google Sheets client and get worksheet.

        Args:
            spreadsheet_id: The ID of the Google Spreadsheet
            sheet_name: Name of the worksheet to access/create
            creds_json: Dictionary containing Google service account credentials
            create_sheet: If True, create the sheet if it doesn't exist

        Returns:
            Tuple containing (client, worksheet)

        Raises:
            ValueError: If sheet doesn't exist and create_sheet is False
        """
        client = service_account_from_dict(creds_json)
        spreadsheet = client.open_by_key(spreadsheet_id)

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except Exception as e:
            if create_sheet:
                # Create with minimal size - will be resized as needed
                worksheet = spreadsheet.add_worksheet(sheet_name, 1, 1)
            else:
                raise ValueError(f"Sheet '{sheet_name}' does not exist and create_sheet is False") from e

        return client, worksheet

    @staticmethod
    def _clear_sheet_data(worksheet: Any, current_rows: int, required_cols: int,
                          start_row: int, erase_whole: bool) -> None:
        """
        Clear sheet data based on parameters.

        Args:
            worksheet: Google Sheets worksheet
            current_rows: Current number of rows in sheet
            required_cols: Number of columns needed
            start_row: First row to clear from
            erase_whole: If True, clear all columns; if False, clear only required columns
        """
        if current_rows >= start_row:
            if erase_whole:
                worksheet.batch_clear([f"{start_row}:{current_rows}"])
            else:
                end_col = chr(64 + required_cols)  # Convert column number to letter (A=65)
                worksheet.batch_clear([f"A{start_row}:{end_col}{current_rows}"])

    @staticmethod
    def _format_date_columns(client: Any, worksheet: Any, date_columns: List[int],
                             start_row: int, required_rows: int) -> None:
        """
        Format date columns with proper date format.

        Args:
            client: Google Sheets client
            worksheet: Target worksheet
            date_columns: List of column indices containing dates
            start_row: First row to format
            required_rows: Total number of rows to format
        """
        if not date_columns:
            return

        spreadsheet = client.open_by_key(worksheet.spreadsheet.id)
        # Create format requests for each date column
        format_requests = [{
            "requests": [{
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": start_row - 1,  # 0-based index
                        "endRowIndex": required_rows,
                        "startColumnIndex": col_idx,
                        "endColumnIndex": col_idx + 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "DATE",
                                "pattern": "yyyy-mm-dd"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            }]
        } for col_idx in date_columns]

        # Apply formatting
        for request in format_requests:
            spreadsheet.batch_update(request)

    @staticmethod
    def df_to_sheets(
            df: DataFrame,
            spreadsheet_id: str,
            sheet_name: str,
            creds_json: Dict,
            keep_header: bool = False,
            erase_whole: bool = True,
            create_sheet: bool = True
    ) -> None:
        """
        Transfer data from Spark DataFrame to Google Sheets while preserving column structure.

        Args:
            df: Spark DataFrame containing the data to transfer
            spreadsheet_id: The ID of the Google Spreadsheet (from the URL)
            sheet_name: Name of the worksheet to update
            creds_json: Dictionary containing Google service account credentials
            keep_header: If True, preserve the first row of the sheet
            erase_whole: If True, clear all columns and rows (maybe skipping first based on keep_header)
            create_sheet: If True, create the sheet if it doesn't exist. If False, raise an error
        """
        from .utils import prepare_data

        client, worksheet = GPP._init_sheets_client(spreadsheet_id, sheet_name, creds_json, create_sheet)
        converted_data, date_columns, header = prepare_data(df, keep_header)

        current_rows = len(worksheet.col_values(1))
        required_rows = len(converted_data) + (1 if keep_header else 0)
        required_cols = len(header)
        start_row = 2 if keep_header else 1

        GPP._clear_sheet_data(worksheet, current_rows, required_cols, start_row, erase_whole)

        if current_rows < required_rows:
            worksheet.add_rows(required_rows - current_rows)

        update_range = f'A2:{chr(64 + required_cols)}{len(converted_data) + 1}' if keep_header else 'A1'
        worksheet.update(update_range, converted_data, value_input_option='USER_ENTERED')

        GPP._format_date_columns(client, worksheet, date_columns, start_row, required_rows)
        worksheet.resize(rows=max(required_rows, 1))

    @staticmethod
    def df_append_to_sheets(
            df: DataFrame,
            spreadsheet_id: str,
            sheet_name: str,
            creds_json: Dict,
            keep_header: bool = False,
            create_sheet: bool = True
    ) -> None:
        """
        Append data from Spark DataFrame to Google Sheets while preserving column structure.

        Args:
            df: Spark DataFrame containing the data to append
            spreadsheet_id: The ID of the Google Spreadsheet (from the URL)
            sheet_name: Name of the worksheet to update
            creds_json: Dictionary containing Google service account credentials
            keep_header: If True, preserve existing header. If False, use DataFrame's header
            create_sheet: If True, create the sheet if it doesn't exist. If False, raise an error
        """
        from .utils import prepare_data

        # Initialize client and worksheet
        client, worksheet = GPP._init_sheets_client(spreadsheet_id, sheet_name, creds_json, create_sheet)

        # Get current data
        current_rows = len(worksheet.col_values(1))

        if current_rows == 0:
            # Sheet is empty, treat it as a new sheet
            GPP.df_to_sheets(
                df=df,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                creds_json=creds_json,
                keep_header=False,  # We're starting fresh
                create_sheet=False  # Sheet already exists
            )
            return

        # Convert DataFrame to lists with proper type conversion
        converted_data, date_columns, header = prepare_data(df, keep_header=True)

        # Get current sheet properties
        existing_header = worksheet.row_values(1)
        current_col_count = len(existing_header) if existing_header else 0
        required_cols = len(header)

        # Add columns if needed
        if required_cols > current_col_count:
            worksheet.resize(cols=required_cols)

        # Calculate start row for new data (always after existing data)
        start_row = current_rows + 1

        # Calculate required space
        data_rows = len(converted_data)
        required_rows = current_rows + data_rows

        # Add rows if needed
        if worksheet.row_count < required_rows:
            worksheet.add_rows(required_rows - worksheet.row_count)

        # Update the data first
        end_col = chr(64 + required_cols)
        update_range = f'A{start_row}:{end_col}{required_rows}'
        worksheet.update(update_range, converted_data, value_input_option='USER_ENTERED')

        # If not keeping header, update it after appending data
        if not keep_header:
            worksheet.update('A1', [header], value_input_option='USER_ENTERED')

        # Format date columns
        GPP._format_date_columns(
            client,
            worksheet,
            date_columns,
            start_row,
            required_rows
        )

    @staticmethod
    def df_overlap_to_sheets(
            df: DataFrame,
            spreadsheet_id: str,
            sheet_name: str,
            creds_json: Dict,
            update_config: Dict,
            keep_header: bool = True,
            create_sheet: bool = True
    ) -> None:
        """
        Update sheet with selective deletion and appending based on configuration.

        Args:
            df: Spark DataFrame containing the data to append
            spreadsheet_id: The ID of the Google Spreadsheet
            sheet_name: Name of the worksheet to update
            creds_json: Dictionary containing Google service account credentials
            update_config: Configuration for update operations
                Format: {
                    "operations": [
                        {"type": "sort", "column": "A", "direction": "asc"},
                        {"type": "delete_from", "column": "A", "value": "2025-02-01", "inclusive": True},
                        # Other supported operations:
                        # {"type": "delete_range", "column": "A", "start_value": x, "end_value": y, "inclusive": True},
                        # {"type": "delete_where", "column": "A", "value": x, "operator": "eq"}
                    ]
                }
                Function references can be used for values:
                {"value": {"function": "MIN", "source": "dataframe", "column": "A"}}
            keep_header: If True, preserve existing header
            create_sheet: If True, create the sheet if it doesn't exist
        """
        from .utils import prepare_data
        from .operations import process_update_config, apply_update_operations

        # Initialize client and worksheet
        client, worksheet = GPP._init_sheets_client(spreadsheet_id, sheet_name, creds_json, create_sheet)

        # If sheet is empty, just do a regular update
        current_rows = len(worksheet.col_values(1))
        if current_rows == 0:
            GPP.df_to_sheets(
                df=df,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                creds_json=creds_json,
                keep_header=False,  # Empty sheet, so no header to keep
                erase_whole=True,
                create_sheet=False  # We already created if needed
            )
            return

        # Process configuration to resolve function references
        processed_config = process_update_config(update_config, df, worksheet)

        # Apply operations and get the row where new data should start
        start_row = apply_update_operations(processed_config, worksheet)

        # Convert DataFrame to lists with proper type conversion
        converted_data, date_columns, header = prepare_data(df, keep_header=True)

        # Get current sheet properties after operations
        current_col_count = len(worksheet.row_values(1)) if worksheet.row_values(1) else 0
        required_cols = len(header)

        # Add columns if needed
        if required_cols > current_col_count:
            worksheet.resize(cols=required_cols)

        # Calculate required space
        data_rows = len(converted_data)
        required_rows = start_row - 1 + data_rows

        # Add rows if needed
        if worksheet.row_count < required_rows:
            worksheet.add_rows(required_rows - worksheet.row_count)

        # Update the data
        end_col = chr(64 + required_cols)  # Convert column number to letter (A=65)
        update_range = f'A{start_row}:{end_col}{required_rows}'
        worksheet.update(update_range, converted_data, value_input_option='USER_ENTERED')

        # Format date columns
        GPP._format_date_columns(
            client,
            worksheet,
            date_columns,
            start_row,
            required_rows
        )

    @staticmethod
    def set_config(spreadsheet_id: str, key: str, value: str, creds_json: Dict, sheet_name: str = "CONFIG") -> int:
        """
        Find a key in column A of the specified sheet and update its corresponding value in column B.

        Args:
            spreadsheet_id: The ID of the Google Spreadsheet
            key: The key to search for in column A
            value: The value to set in column B
            creds_json: Dictionary containing Google service account credentials
            sheet_name: Name of the worksheet (defaults to "CONFIG")

        Returns:
            int: 0 if successful, 1 if an error occurs
        """
        try:
            # Initialize the client and get the worksheet
            client, worksheet = GPP._init_sheets_client(spreadsheet_id, sheet_name, creds_json)

            # Get all values from column A
            keys = worksheet.col_values(1)  # Column A

            # Find the row number for the key
            try:
                row_num = keys.index(key) + 1  # Adding 1 because sheets are 1-indexed
            except ValueError:
                # Key not found, append new row
                row_num = len(keys) + 1
                worksheet.update(f'A{row_num}', [[key]])

            # Update the value in column B
            worksheet.update(f'B{row_num}', [[value]])

            return 0

        except Exception as e:
            print(f"Error in set_config: {str(e)}")
            return 1

    @staticmethod
    def debug(text="This is debug"):
        print(text)