import pandas as pd
import calendar
import os
import numpy as np
import re
from datetime import datetime, timedelta
import subprocess
import json
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor

class dataprocessing:
    
    def help(self):
        
        print("\n1. get_wd_levels")
        print("   - Description: Get the working directory with the option of moving up parents.")
        print("   - Usage: get_wd_levels(levels)")
        print("   - Example: get_wd_levels(0)")

        print("\n2. aggregate_daily_to_wc_long")
        print("   - Description: Aggregates daily data into weekly data, grouping and summing specified columns, starting on a specified day of the week.")
        print("   - Usage: aggregate_daily_to_wc_long(df, date_column, group_columns, sum_columns, wc, aggregation='sum')")
        print("   - Example: aggregate_daily_to_wc_long(df, 'date', ['platform'], ['cost', 'impressions', 'clicks'], 'mon', 'average')")

        print("\n3. convert_monthly_to_daily")
        print("   - Description: Converts monthly data in a DataFrame to daily data by expanding and dividing the numeric values.")
        print("   - Usage: convert_monthly_to_daily(df, date_column, divide=True)")
        print("   - Example: convert_monthly_to_daily(df, 'date')")

        print("\n4. week_of_year_mapping")
        print("   - Description: Converts a week column in 'yyyy-Www' or 'yyyy-ww' format to week commencing date.")
        print("   - Usage: week_of_year_mapping(df, week_col, start_day_str)")
        print("   - Example: week_of_year_mapping(df, 'week', 'mon')")

        print("\n5. rename_cols")
        print("   - Description: Renames columns in a pandas DataFrame with a specified prefix or format.")
        print("   - Usage: rename_cols(df, name='ame_')")
        print("   - Example: rename_cols(df, 'ame_facebook')")

        print("\n6. merge_new_and_old")
        print("   - Description: Creates a new DataFrame by merging old and new dataframes based on a cutoff date.")
        print("   - Usage: merge_new_and_old(old_df, old_col, new_df, new_col, cutoff_date, date_col_name='OBS')")
        print("   - Example: merge_new_and_old(df1, 'old_col', df2, 'new_col', '2023-01-15')")

        print("\n7. merge_dataframes_on_column")
        print("   - Description: Merge a list of DataFrames on a common column.")
        print("   - Usage: merge_dataframes_on_column(dataframes, common_column='OBS', merge_how='outer')")
        print("   - Example: merge_dataframes_on_column([df1, df2, df3], common_column='OBS', merge_how='outer')")

        print("\n8. merge_and_update_dfs")
        print("   - Description: Merges two dataframes, updating columns from the second dataframe where values are available.")
        print("   - Usage: merge_and_update_dfs(df1, df2, key_column)")
        print("   - Example: merge_and_update_dfs(processed_facebook, finalised_meta, 'OBS')")

        print("\n9. convert_us_to_uk_dates")
        print("   - Description: Convert a DataFrame column with mixed US and UK date formats to datetime.")
        print("   - Usage: convert_us_to_uk_dates(df, date_col)")
        print("   - Example: convert_us_to_uk_dates(df, 'date')")

        print("\n10. combine_sheets")
        print("    - Description: Combines multiple DataFrames from a dictionary into a single DataFrame.")
        print("    - Usage: combine_sheets(all_sheets)")
        print("    - Example: combine_sheets({'Sheet1': df1, 'Sheet2': df2})")

        print("\n11. pivot_table")
        print("    - Description: Dynamically pivots a DataFrame based on specified columns.")
        print("    - Usage: pivot_table(df, index_col, columns, values_col, filters_dict=None, fill_value=0, aggfunc='sum', margins=False, margins_name='Total', datetime_trans_needed=True, reverse_header_order=False, fill_missing_weekly_dates=False, week_commencing='W-MON')")
        print("    - Example: pivot_table(df, 'OBS', 'Channel Short Names', 'Value', filters_dict={'Master Include': ' == 1'}, fill_value=0)")

        print("\n12. apply_lookup_table_for_columns")
        print("    - Description: Maps substrings in columns to new values based on a dictionary.")
        print("    - Usage: apply_lookup_table_for_columns(df, col_names, to_find_dict, if_not_in_dict='Other', new_column_name='Mapping')")
        print("    - Example: apply_lookup_table_for_columns(df, col_names, {'spend': 'spd'}, if_not_in_dict='Other', new_column_name='Metrics Short')")

        print("\n13. aggregate_daily_to_wc_wide")
        print("   - Description: Aggregates daily data into weekly data and pivots it to wide format.")
        print("   - Usage: aggregate_daily_to_wc_wide(df, date_column, group_columns, sum_columns, wc='sun', aggregation='sum', include_totals=False)")
        print("   - Example: aggregate_daily_to_wc_wide(df, 'date', ['platform'], ['cost', 'impressions'], 'mon', 'average', True)")

        print("\n14. merge_cols_with_seperator")
        print("   - Description: Merges multiple columns in a DataFrame into one column with a specified separator.")
        print("   - Usage: merge_cols_with_seperator(df, col_names, separator='_', output_column_name='Merged')")
        print("   - Example: merge_cols_with_seperator(df, ['Campaign', 'Product'], separator='|', output_column_name='Merged Columns')")

        print("\n15. check_sum_of_df_cols_are_equal")
        print("   - Description: Checks if the sum of two columns in two DataFrames are equal and provides the difference.")
        print("   - Usage: check_sum_of_df_cols_are_equal(df_1, df_2, cols_1, cols_2)")
        print("   - Example: check_sum_of_df_cols_are_equal(df_1, df_2, 'Media Cost', 'Spend')")

        print("\n16. convert_2_df_cols_to_dict")
        print("   - Description: Creates a dictionary from two DataFrame columns.")
        print("   - Usage: convert_2_df_cols_to_dict(df, key_col, value_col)")
        print("   - Example: convert_2_df_cols_to_dict(df, 'Campaign', 'Channel')")

        print("\n17. create_FY_and_H_columns")
        print("   - Description: Adds financial year and half-year columns to a DataFrame based on a start date.")
        print("   - Usage: create_FY_and_H_columns(df, index_col, start_date, starting_FY, short_format='No', half_years='No', combined_FY_and_H='No')")
        print("   - Example: create_FY_and_H_columns(df, 'Week', '2022-10-03', 'FY2023', short_format='Yes')")

        print("\n18. keyword_lookup_replacement")
        print("   - Description: Updates values in a column based on a lookup dictionary with conditional logic.")
        print("   - Usage: keyword_lookup_replacement(df, col, replacement_rows, cols_to_merge, replacement_lookup_dict, output_column_name='Updated Column')")
        print("   - Example: keyword_lookup_replacement(df, 'channel', 'Paid Search Generic', ['channel', 'segment'], lookup_dict, output_column_name='Channel New')")

        print("\n19. create_new_version_of_col_using_LUT")
        print("   - Description: Creates a new column based on a lookup table applied to an existing column.")
        print("   - Usage: create_new_version_of_col_using_LUT(df, keys_col, value_col, dict_for_specific_changes, new_col_name='New Version of Old Col')")
        print("   - Example: create_new_version_of_col_using_LUT(df, 'Campaign Name', 'Campaign Type', lookup_dict)")        

        print("\n20. convert_df_wide_2_long")
        print("   - Description: Converts a wide-format DataFrame into a long-format DataFrame.")
        print("   - Usage: convert_df_wide_2_long(df, value_cols, variable_col_name='Stacked', value_col_name='Value')")
        print("   - Example: convert_df_wide_2_long(df, ['col1', 'col2'], variable_col_name='Var', value_col_name='Val')")

        print("\n21. manually_edit_data")
        print("   - Description: Manually updates specified cells in a DataFrame based on filters.")
        print("   - Usage: manually_edit_data(df, filters_dict, col_to_change, new_value, change_in_existing_df_col='No', new_col_to_change_name='New', manual_edit_col_name=None, add_notes='No', existing_note_col_name=None, note=None)")
        print("   - Example: manually_edit_data(df, {'col1': '== 1'}, 'col2', 'new_val', add_notes='Yes', note='Manual Update')")

        print("\n22. format_numbers_with_commas")
        print("   - Description: Formats numerical columns with commas and a specified number of decimal places.")
        print("   - Usage: format_numbers_with_commas(df, decimal_length_chosen=2)")
        print("   - Example: format_numbers_with_commas(df, decimal_length_chosen=1)")

        print("\n23. filter_df_on_multiple_conditions")
        print("   - Description: Filters a DataFrame based on multiple column conditions.")
        print("   - Usage: filter_df_on_multiple_conditions(df, filters_dict)")
        print("   - Example: filter_df_on_multiple_conditions(df, {'col1': '>= 5', 'col2': '== 'val''})")

        print("\n24. read_and_concatenate_files")
        print("   - Description: Reads and concatenates files from a specified folder into a single DataFrame.")
        print("   - Usage: read_and_concatenate_files(folder_path, file_type='csv')")
        print("   - Example: read_and_concatenate_files('/path/to/files', file_type='xlsx')")

        print("\n25. upgrade_outdated_packages")
        print("   - Description: Upgrades all outdated Python packages except specified ones.")
        print("   - Usage: upgrade_outdated_packages(exclude_packages=['twine'])")
        print("   - Example: upgrade_outdated_packages(exclude_packages=['pip', 'setuptools'])")

        print("\n26. convert_mixed_formats_dates")
        print("   - Description: Converts mixed-format date columns into standardized datetime format.")
        print("   - Usage: convert_mixed_formats_dates(df, column_name)")
        print("   - Example: convert_mixed_formats_dates(df, 'date_col')")

        print("\n27. fill_weekly_date_range")
        print("   - Description: Fills in missing weekly dates in a DataFrame with a specified frequency.")
        print("   - Usage: fill_weekly_date_range(df, date_column, freq='W-MON')")
        print("   - Example: fill_weekly_date_range(df, 'date_col')")

        print("\n28. add_prefix_and_suffix")
        print("   - Description: Adds prefixes and/or suffixes to column names, with an option to exclude a date column.")
        print("   - Usage: add_prefix_and_suffix(df, prefix='', suffix='', date_col=None)")
        print("   - Example: add_prefix_and_suffix(df, prefix='pre_', suffix='_suf', date_col='date_col')")

        print("\n29. create_dummies")
        print("   - Description: Creates dummy variables for columns, with an option to add a total dummy column.")
        print("   - Usage: create_dummies(df, date_col=None, dummy_threshold=0, add_total_dummy_col='No', total_col_name='total')")
        print("   - Example: create_dummies(df, date_col='date_col', dummy_threshold=1)")

        print("\n30. replace_substrings")
        print("   - Description: Replaces substrings in a column based on a dictionary, with options for case conversion and new column creation.")
        print("   - Usage: replace_substrings(df, column, replacements, to_lower=False, new_column=None)")
        print("   - Example: replace_substrings(df, 'text_col', {'old': 'new'}, to_lower=True, new_column='updated_text')")

        print("\n31. add_total_column")
        print("   - Description: Adds a total column to a DataFrame by summing values across columns, optionally excluding one.")
        print("   - Usage: add_total_column(df, exclude_col=None, total_col_name='Total')")
        print("   - Example: add_total_column(df, exclude_col='date_col')")

        print("\n32. apply_lookup_table_based_on_substring")
        print("   - Description: Categorizes text in a column using a lookup table based on substrings.")
        print("   - Usage: apply_lookup_table_based_on_substring(df, column_name, category_dict, new_col_name='Category', other_label='Other')")
        print("   - Example: apply_lookup_table_based_on_substring(df, 'text_col', {'sub1': 'cat1', 'sub2': 'cat2'})")

        print("\n33. compare_overlap")
        print("   - Description: Compares overlapping periods between two DataFrames and summarizes differences.")
        print("   - Usage: compare_overlap(df1, df2, date_col)")
        print("   - Example: compare_overlap(df1, df2, 'date_col')")

        print("\n34. week_commencing_2_week_commencing_conversion_isoweekday")
        print("   - Description: Maps dates to the start of the current ISO week based on a specified weekday.")
        print("   - Usage: week_commencing_2_week_commencing_conversion_isoweekday(df, date_col, week_commencing='mon')")
        print("   - Example: week_commencing_2_week_commencing_conversion_isoweekday(df, 'date_col', week_commencing='fri')")
        
        print("\n35. seasonality_feature_extraction")
        print("   - Description: Splits data into train/test sets, trains XGBoost and Random Forest on all features, extracts top features based on feature importance, merges them, optionally retrains models on top and combined features, and returns a dict of results.")
        print("   - Usage: seasonality_feature_extraction(df, kpi_var, n_features=10, test_size=0.1, random_state=42, shuffle=False)")
        print("   - Example: seasonality_feature_extraction(df, 'kpi_total_sales', n_features=5, test_size=0.2, random_state=123, shuffle=True)")

    def get_wd_levels(self, levels):
        """
        Gets the current wd of whoever is working on it and gives the options to move the number of levels up.

        Parameters:
        - data_frame: pandas DataFrame
            The input data frame.
        - num_rows_to_remove: int
            The number of levels to move up pathways.

        Returns:
        - Current wd
        """

        directory = os.getcwd()
        for _ in range(levels):
            directory = os.path.dirname(directory)
        return directory
    
    def aggregate_daily_to_wc_long(self, df : pd.DataFrame, date_column : str, group_columns : list[str], sum_columns : list[str], wc : str = 'sun', aggregation : str = 'sum') -> pd.DataFrame:
        """
        Aggregates daily data into weekly data, starting on a specified day of the week, 
        and groups the data by additional specified columns. It aggregates specified numeric columns 
        by summing, averaging, or counting them, and pivots the data to create separate columns for each combination 
        of the group columns and sum columns. NaN values are replaced with 0 and the index is reset. 
        The day column is renamed from 'Day' to 'OBS'.

        Parameters:
        - df: pandas DataFrame
            The input DataFrame containing daily data.
        - date_column: string
            The name of the column in the DataFrame that contains date information.
        - group_columns: list of strings
            Additional column names to group by along with the weekly grouping.
        - sum_columns: list of strings
            Numeric column names to be aggregated during aggregation.
        - wc: string
            The week commencing day (e.g., 'sun' for Sunday, 'mon' for Monday).
        - aggregation: string, optional (default 'sum')
            Aggregation method, either 'sum', 'average', or 'count'.

        Returns:
        - pandas DataFrame
            A new DataFrame with weekly aggregated data. The index is reset,
            and columns represent the grouped and aggregated metrics. The DataFrame 
            is in long format, with separate columns for each combination of 
            grouped metrics.
        """

        # Map the input week commencing day to a weekday number (0=Monday, 6=Sunday)
        days = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        if wc.lower() not in days:
            return print(f"Incorrect week commencing day input: '{wc}'. Please choose a valid day of the week (e.g., 'sun', 'mon', etc.).")

        start_day = days[wc.lower()]

        # Make a copy of the DataFrame
        df_copy = df.copy()

        # Convert the date column to datetime
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])

        # Determine the start of each week
        df_copy['week_start'] = df_copy[date_column].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - start_day) % 7))

        # Convert sum_columns to numeric and fill NaNs with 0, retaining decimal values
        for col in sum_columns:
            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce').fillna(0)

        # Group by the new week start column and additional columns, then aggregate the numeric columns
        if aggregation == 'average':
            grouped = df_copy.groupby(['week_start'] + group_columns)[sum_columns].mean().reset_index()
        elif aggregation == 'count':
            grouped = df_copy.groupby(['week_start'] + group_columns)[sum_columns].count().reset_index()
        else:  # Default to 'sum' if any other value is provided
            grouped = df_copy.groupby(['week_start'] + group_columns)[sum_columns].sum().reset_index()

        # Rename 'week_start' column to 'OBS'
        grouped = grouped.rename(columns={'week_start': 'OBS'})

        return grouped
    
    def convert_monthly_to_daily(self, df, date_column, divide = True):
        """
        Convert a DataFrame with monthly data to daily data.
        This function takes a DataFrame and a date column, then it expands each
        monthly record into daily records by dividing the numeric values by the number of days in that month.

        :param df: DataFrame with monthly data.
        :param date_column: The name of the column containing the date.
        :param divide: boolean divide by the number of days in a month (default True)
        :return: A new DataFrame with daily data.
        """

        # Convert date_column to datetime
        df[date_column] = pd.to_datetime(df[date_column])

        # Initialize an empty list to hold the daily records
        daily_records = []

        # Iterate over each row in the DataFrame
        for _, row in df.iterrows():
            # Calculate the number of days in the month
            num_days = calendar.monthrange(row[date_column].year, row[date_column].month)[1]

            # Create a new record for each day of the month
            for day in range(1, num_days + 1):
                daily_row = row.copy()
                daily_row[date_column] = row[date_column].replace(day=day)

                # Divide each numeric value by the number of days in the month
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]) and col != date_column:
                        if divide is True:
                            daily_row[col] = row[col] / num_days
                        else: 
                            daily_row[col] = row[col]
                daily_records.append(daily_row)

        # Convert the list of daily records into a DataFrame
        daily_df = pd.DataFrame(daily_records)
        
        return daily_df
    
    def week_of_year_mapping(self,df, week_col, start_day_str):

        # Mapping of string day names to day numbers (1 for Monday, 7 for Sunday)
        day_mapping = {
            'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7
        }

        # Convert the day string to a number, or raise an error if not valid
        start_day = day_mapping.get(start_day_str.lower())
        if start_day is None:
            raise ValueError(f"Invalid day input: '{start_day_str}'. Please use one of 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'.")

        # Function to convert week number to start date of the week
        def week_to_startdate(week_str, start_day):
            year, week = map(int, week_str.split('-W'))
            first_day_of_year = datetime(year, 1, 1)
            first_weekday_of_year = first_day_of_year.weekday()  # Monday is 0 and Sunday is 6

            # Calculate days to adjust to the desired start day of the week
            days_to_adjust = (start_day - 1 - first_weekday_of_year) % 7
            start_of_iso_week = first_day_of_year + timedelta(days=days_to_adjust)

            # Calculate the start of the desired week
            start_of_week = start_of_iso_week + timedelta(weeks=week - 1)
            return start_of_week

        # Apply the function to each row in the specified week column
        df['OBS'] = df[week_col].apply(lambda x: week_to_startdate(x, start_day)).dt.strftime('%d/%m/%Y')
        return df
        
    def rename_cols(self, df, name = 'ame_'):
        new_columns = {}
        for col in df.columns:
            if col != 'OBS':
                new_col_name = name + col.replace(" ", "_").lower()
            else:
                new_col_name = col
            new_columns[col] = new_col_name
        return df.rename(columns=new_columns)
    
    def merge_new_and_old(self, old_df, old_col, new_df, new_col, cutoff_date, date_col_name='OBS'):
        """
        Creates a new DataFrame with two columns: one for dates and one for merged numeric values.
        Merges numeric values from specified columns in the old and new DataFrames based on a given cutoff date.

        Parameters:
        - old_df: pandas DataFrame
            The old DataFrame from which to take the numeric values up to the specified date.
        - old_col: str
            The name of the numeric column in the old DataFrame whose values are to be taken.
        - new_df: pandas DataFrame
            The new DataFrame from which to take the numeric values from the specified date onwards.
        - new_col: str
            The name of the numeric column in the new DataFrame whose values are to be taken.
        - cutoff_date: str
            The cut-off date in 'YYYY-MM-DD' format to split the data between the two DataFrames.
        - date_col_name: str, optional (default 'OBS')
            The name of the date column in both DataFrames.

        Returns:
        - pandas DataFrame
            A new DataFrame with two columns: 'Date' and a column named after 'new_col' containing merged numeric values.
        """

        # Convert date columns in both dataframes to datetime for comparison
        old_df[date_col_name] = pd.to_datetime(old_df[date_col_name])
        new_df[date_col_name] = pd.to_datetime(new_df[date_col_name])

        # Convert the cutoff date string to datetime
        cutoff_date = pd.to_datetime(cutoff_date)

        # Split old and new dataframes based on the cutoff date
        old_values = old_df[old_df[date_col_name] <= cutoff_date]
        new_values = new_df[new_df[date_col_name] > cutoff_date]

        # Create a new DataFrame with two columns: 'Date' and a column named after 'new_col'
        merged_df = pd.DataFrame({
            'OBS': pd.concat([old_values[date_col_name], new_values[date_col_name]], ignore_index=True),
            new_col: pd.concat([old_values[old_col], new_values[new_col]], ignore_index=True)
        })

        return merged_df
    
    def merge_dataframes_on_column(self, dataframes, common_column='OBS', merge_how='outer'):
        """
        Merge a list of DataFrames on a common column.

        Parameters:
        - dataframes: A list of DataFrames to merge.
        - common_column: The name of the common column to merge on.
        - merge_how: The type of merge to perform ('inner', 'outer', 'left', or 'right').

        Returns:
        - A merged DataFrame.
        """
        if not dataframes:
            return None
        
        merged_df = dataframes[0]  # Start with the first DataFrame

        for df in dataframes[1:]:
            merged_df = pd.merge(merged_df, df, on=common_column, how=merge_how)

        # Check if the common column is of datetime dtype
        if merged_df[common_column].dtype == 'datetime64[ns]':
            merged_df[common_column] = pd.to_datetime(merged_df[common_column])
        merged_df = merged_df.sort_values(by=common_column)
        merged_df = merged_df.fillna(0)
        
        return merged_df
    
    def merge_and_update_dfs(self, df1, df2, key_column):
        """
        Merges two dataframes on a key column, updates the first dataframe's columns with the second's where available,
        and returns a dataframe sorted by the key column.

        Parameters:
        df1 (DataFrame): The first dataframe to merge (e.g., processed_facebook).
        df2 (DataFrame): The second dataframe to merge (e.g., finalised_meta).
        key_column (str): The name of the column to merge and sort by (e.g., 'OBS').

        Returns:
        DataFrame: The merged and updated dataframe.
        """

        # Sort both DataFrames by the key column
        df1_sorted = df1.sort_values(by=key_column)
        df2_sorted = df2.sort_values(by=key_column)

        # Perform the full outer merge
        merged_df = pd.merge(df1_sorted, df2_sorted, on=key_column, how='outer', suffixes=('', '_finalised'))

        # Update with non-null values from df2
        for column in merged_df.columns:
            if column.endswith('_finalised'):
                original_column = column.replace('_finalised', '')
                merged_df.loc[merged_df[column].notnull(), original_column] = merged_df.loc[merged_df[column].notnull(), column]
                merged_df.drop(column, axis=1, inplace=True)

        # Sort the merged DataFrame by the key column
        merged_df.sort_values(by=key_column, inplace=True)

        # Handle null values (optional, can be adjusted as needed)
        merged_df.fillna(0, inplace=True)

        return merged_df
    
    def convert_us_to_uk_dates(self, df, date_col):
        """
        Processes the date column of a DataFrame to remove hyphens and slashes, 
        and converts it to a datetime object.
        
        Parameters:
        df (pd.DataFrame): The DataFrame containing the date column.
        date_col (str): The name of the date column.
        
        Returns:
        pd.DataFrame: The DataFrame with the processed date column.
        """
        df[date_col] = df[date_col].str.replace(r'[-/]', '', regex=True)
        df[date_col] = pd.to_datetime(
            df[date_col].str.slice(0, 2) + '/' +
            df[date_col].str.slice(2, 4) + '/' +
            df[date_col].str.slice(4, 8),
            format='%m/%d/%Y'
        )
        return df

    def combine_sheets(self, all_sheets):
        """
        Combines multiple DataFrames from a dictionary into a single DataFrame.
        Adds a column 'SheetName' indicating the origin sheet of each row.

        Parameters:
        all_sheets (dict): A dictionary of DataFrames, typically read from an Excel file with multiple sheets.

        Returns:
        DataFrame: A concatenated DataFrame with an additional 'SheetName' column.
        """
        combined_df = pd.DataFrame()

        for sheet_name, df in all_sheets.items():
            df['SheetName'] = sheet_name 
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        return combined_df
    
    def pivot_table(self, df, index_col, columns, values_col, filters_dict=None, fill_value=0, aggfunc="sum", margins=False, margins_name="Total", datetime_trans_needed=True, date_format="%Y-%m-%d", reverse_header_order=False, fill_missing_weekly_dates=True, week_commencing="W-MON"):       
        """
        Provides the ability to create pivot tables, filtering the data to get to data you want and then pivoting on certain columns

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            index_col (str): Name of Column for your pivot table to index on
            columns (str or list): Name of Column(s) for your pivot table. Can be a single column or a list of columns.
            values_col (str or list): Name of Values Column(s) for your pivot table. Can be a single column or a list of columns.
            filters_dict (dict, optional): Dictionary of conditions for the boolean mask i.e. what to filter your df on to get to your chosen cell. Defaults to None
            fill_value (int, optional): The value to replace nan with. Defaults to 0.
            aggfunc (str, optional): The method on which to aggregate the values column. Defaults to sum.
            margins (bool, optional): Whether the pivot table needs a total rows and column. Defaults to False.
            margins_name (str, optional): The name of the Totals columns. Defaults to "Total".
            datetime_trans_needed (bool, optional): Whether the index column needs to be transformed into datetime format. Defaults to False.
            reverse_header_order (bool, optional): Reverses the order of the column headers. Defaults to False.
            fill_missing_weekly_dates (bool, optional): Fills in any weekly missing dates. Defaults to False.
            week_commencing (str,optional): Fills in missing weeks if option is specified. Defaults to 'W-MON'.

        Returns:
            pandas.DataFrame: The pivot table specified
        """
        # Validate inputs
        if index_col not in df.columns:
            raise ValueError(f"index_col '{index_col}' not found in DataFrame.")

        columns = [columns] if isinstance(columns, str) else columns
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"columns '{col}' not found in DataFrame.")

        values_col = [values_col] if isinstance(values_col, str) else values_col
        for col in values_col:
            if col not in df.columns:
                raise ValueError(f"values_col '{col}' not found in DataFrame.")

        # Apply filters if provided
        if filters_dict:
            df_filtered = self.filter_df_on_multiple_conditions(df, filters_dict)
        else:
            df_filtered = df.copy()

        # Ensure index column is in datetime format if needed
        if datetime_trans_needed:
            df_filtered[index_col] = pd.to_datetime(df_filtered[index_col], dayfirst=True)

        # Create the pivot table
        pivoted_df = df_filtered.pivot_table(
            index=index_col,
            columns=columns,
            values=values_col,
            aggfunc=aggfunc,
            margins=margins,
            margins_name=margins_name,
        )

        # Handle column headers
        if isinstance(pivoted_df.columns, pd.MultiIndex):
            pivoted_df.columns = [
                "_".join(reversed(map(str, col)) if reverse_header_order else map(str, col))
                for col in pivoted_df.columns.values
            ]
        else:
            pivoted_df.columns = pivoted_df.columns.map(str)

        # Reset the index
        pivoted_df.reset_index(inplace=True)

        # Handle sorting and formatting of index column
        if datetime_trans_needed:
            pivoted_df[index_col] = pd.to_datetime(pivoted_df[index_col], errors="coerce")
            pivoted_df.sort_values(by=index_col, inplace=True)
            pivoted_df[index_col] = pivoted_df[index_col].dt.strftime(date_format)

        # Fill missing values
        pivoted_df.fillna(fill_value, inplace=True)

        # Fill missing weekly dates if specified
        if fill_missing_weekly_dates:
            pivoted_df = self.fill_weekly_date_range(pivoted_df, index_col, freq=week_commencing)

        return pivoted_df

    def apply_lookup_table_for_columns(self, df, col_names, to_find_dict, if_not_in_dict="Other", new_column_name="Mapping"):
        """
        Creates a new DataFrame column based on a look up table, possibly with multiple columns to look up on (dictionary of substrings to class mappings).

        Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        col_names (list of str): these are the columns which are used for the lookup. One column or several columns can be inputted as a list, provided there is a merged column to lookup on. If there are multiple columns to look up on then a merged column must be inputted as the key of the dictionary of format e.g. col1|col2|col3
        to_find_dict (dict): your look up table, where keys are the values being looked up, and the values are the resulting mappings. 
        if_not_in_dict (str, optional): default value if no substring matches are found in the look up table dictionary. Defaults to "Other".
        new_column_name (str, optional): name of new column. Defaults to "Mapping".

        Returns:
        pandas.DataFrame: DataFrame with a new column containing the look up table results.
        """

        # Create regex pattern with word boundaries from the dictionary
        regex_pattern = "|".join(r'\b' + re.escape(key) + r'\b' for key in to_find_dict.keys())
        
        # Preprocess DataFrame if multiple columns
        if len(col_names) > 1:
            df["Merged"] = df[col_names].astype(str).apply('|'.join, axis=1)
            col_to_use = "Merged"
        else:
            col_to_use = col_names[0]

        # Extract the first match using the regex pattern
        matches = df[col_to_use].str.extract(f'({regex_pattern})', expand=False, flags=re.IGNORECASE)
        
        # Map the matches to the corresponding values in the dictionary
        df[new_column_name] = matches.str.lower().map({k.lower(): v for k, v in to_find_dict.items()}).fillna(if_not_in_dict)
        
        # Drop intermediate column if created
        if len(col_names) > 1:
            df.drop(columns=["Merged"], inplace=True)

        return df

    def aggregate_daily_to_wc_wide(self, df : pd.DataFrame, date_column : str, group_columns : list[str], sum_columns : list[str], wc : str = 'sun', aggregation : str = 'sum', include_totals : bool = False) -> pd.DataFrame:
        """
        Aggregates daily data into weekly data, starting on a specified day of the week, 
        and groups the data by additional specified columns. It aggregates specified numeric columns 
        by summing, averaging, or counting them, and pivots the data to create separate columns for each combination 
        of the group columns and sum columns. NaN values are replaced with 0 and the index is reset. 
        The day column is renamed from 'Day' to 'OBS'.

        Parameters:
        - df: pandas DataFrame
            The input DataFrame containing daily data.
        - date_column: string
            The name of the column in the DataFrame that contains date information.
        - group_columns: list of strings
            Additional column names to group by along with the weekly grouping.
        - sum_columns: list of strings
            Numeric column names to be aggregated during aggregation.
        - wc: string
            The week commencing day (e.g., 'sun' for Sunday, 'mon' for Monday).
        - aggregation: string, optional (default 'sum')
            Aggregation method, either 'sum', 'average', or 'count'.
        - include_totals: boolean, optional (default False)
            If True, include total columns for each sum_column.

        Returns:
        - pandas DataFrame
            A new DataFrame with weekly aggregated data. The index is reset,
            and columns represent the grouped and aggregated metrics. The DataFrame 
            is in wide format, with separate columns for each combination of 
            grouped metrics.
        """
        
        grouped = self.aggregate_daily_to_wc_long(df, date_column, group_columns, sum_columns, wc, aggregation)
        
        # Pivot the data to wide format
        if group_columns:
            wide_df = grouped.pivot_table(index='OBS', 
                                        columns=group_columns, 
                                        values=sum_columns,
                                        aggfunc='first')
            # Flatten the multi-level column index and create combined column names
            wide_df.columns = ['_'.join(col).strip() for col in wide_df.columns.values]
        else:
            wide_df = grouped.set_index('OBS')

        # Fill NaN values with 0
        wide_df = wide_df.fillna(0)

        # Adding total columns for each unique sum_column, if include_totals is True
        if include_totals:
            for col in sum_columns:
                total_column_name = f'Total {col}'
                if group_columns:
                    columns_to_sum = [column for column in wide_df.columns if col in column]
                else:
                    columns_to_sum = [col]
                wide_df[total_column_name] = wide_df[columns_to_sum].sum(axis=1)

        # Reset the index of the final DataFrame
        wide_df = wide_df.reset_index()

        return wide_df

    def merge_cols_with_seperator(self, df, col_names,seperator='_',output_column_name = "Merged",starting_prefix_str=None,ending_prefix_str=None):
        """
        Creates a new column in the dataframe that merges 2 or more columns together with a "_" seperator, possibly to be used for a look up table where multiple columns are being looked up

        Parameters:
        df (pandas.DataFrame): Dataframe to make changes to.
        col_names (list): list of columm names ot merge.
        seperator (str, optional): Name of column outputted. Defaults to "_".
        output_column_name (str, optional): Name of column outputted. Defaults to "Merged".
        starting_prefix_str (str, optional): string of optional text to be added before the merged column str value
        ending_prefix_str (str, optional): string of optional text to be added after the merged column str value

        Raises:
        ValueError: if more less than two column names are inputted in the list there is nothing to merge on

        Returns:
        pandas.DataFrame: DataFrame with additional merged column
        """
        # Specify more than one column must be entered
        if len(col_names) < 2:
            raise ValueError("2 or more columns must be specified to merge")
        
        # Create a new column with the merged columns
        df[output_column_name] = df[col_names].astype(str).apply(seperator.join, axis=1)

        # Add string before 
        if starting_prefix_str is not None:
            df[output_column_name] = starting_prefix_str + df[output_column_name].astype(str)
        
        # Add string after
        if ending_prefix_str is not None:
            df[output_column_name] = df[output_column_name].astype(str) + ending_prefix_str
                    
        return df

    def check_sum_of_df_cols_are_equal(self, df_1,df_2,cols_1,cols_2):
        """
        Checks the sum of two different dataframe column or columns are equal

        Parameters:
        df_1 (pandas.DataFrame): First dataframe for columnsa to be summed on.
        df_2 (pandas.DataFrame): Second dataframe for columnsa to be summed on.
        cols_1 (list of str): Columns from first dataframe to sum.
        cols_2 (list of str): Columns from second dataframe to sum.

        Returns:
        Tuple: Answer is the true or false answer to whether sums are the same, df_1_sum is the sum of the column/columns in the first dataframe, df_2_sum is the sum of the column/columns in the second dataframe
        """
        # Find the sum of both sets of columns
        df_1_sum = df_1[cols_1].sum().sum()
        df_2_sum = df_2[cols_2].sum().sum()
        
        # If the the two columns are 
        if df_1_sum == df_2_sum:
            Answer = "They are equal"
        if df_1_sum != df_2_sum:
            Answer = "They are different by " + str(df_2_sum-df_1_sum)     
            
        return Answer,df_1_sum,df_2_sum
    
    def convert_2_df_cols_to_dict(self, df, key_col, value_col):
        """
        Create a dictionary mapping from two columns of a DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        key_col (str): The column name to use as keys in the dictionary.
        value_col (str): The column name to use as values in the dictionary.

        Returns:
        dict: A dictionary with keys from 'key_col' and values from 'value_col'.
        """
        if key_col not in df or value_col not in df:
            raise ValueError("Specified columns are not in the DataFrame")

        return {df[key_col].iloc[i]: df[value_col].iloc[i] for i in range(len(df))}
    
    def create_FY_and_H_columns(self, df, index_col, start_date, starting_FY,short_format="No",half_years="No",combined_FY_and_H="No"):
        """
        Creates new DataFrame columns containing companies' Financial Year, Half Years and Financial Half years, based on the start date of the first full financial year 

        Parameters:
        df (pandas.DataFrame): Dataframe to operate on.
        index_col (str): Name of the column to use for datetime
        start_date (str): String used to specify the start date of an FY specified, needs to be of format "yyyy-mm-dd" e.g. 2021-11-31
        starting_FY (str): String used to specify which FY the start date refers to, needs to be formatted LONG e.g. FY2021
        short_format (str, optional): String used to specify if short format is desired (e.g. FY21) or if long format is desired (e.g. FY2021). Defaults to "No".
        half_years (str, optional): String used to specify if half year column is desired. Defaults to "No".
        combined_FY_and_H (str, optional): String used to specify is a combined half year and FY column is desired. Defaults to "No".

        Returns:
        pandas.DataFrame: DataFrame with a new column 'FY' containing the FY as well as, if desired, a half year column and a combined FY half year column.
        """
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Date must be of format yyyy-mm-dd")
            return df
        
        df["OBS"] = pd.to_datetime(df[index_col])
        df["OBS as string"] = df["OBS"].dt.strftime("%Y-%m-%d")

        df[index_col] = pd.to_datetime(df[index_col])

        start_year = int(starting_FY[2:])

        def calculate_FY_vectorized(date_series):
            years_since_start = ((date_series - start_date).dt.days / 364).astype(int)
            fy = 'FY' + (start_year + years_since_start).astype(str)
            if short_format == "Yes":
                fy = 'FY' + fy.str[-2:]
            return fy

        df['FY'] = calculate_FY_vectorized(df[index_col])

        if half_years == "Yes" or combined_FY_and_H == "Yes":
            def calculate_half_year_vectorized(date_series):
                fy_years_since_start = ((date_series - start_date).dt.days / 364).astype(int)
                fy_start_dates = start_date + fy_years_since_start * pd.DateOffset(years=1)
                fy_end_of_h1 = fy_start_dates + pd.DateOffset(weeks=26) - pd.DateOffset(weeks=1)
                half_year = np.where(date_series <= fy_end_of_h1, 'H1', 'H2')
                return half_year
            
            df['Half Years'] = calculate_half_year_vectorized(df[index_col])
        
        if combined_FY_and_H == "Yes":
            df['Financial Half Years'] = df['FY'] + ' ' + df['Half Years']

        return df
    
    def keyword_lookup_replacement(self, df, col, replacement_rows, cols_to_merge, replacement_lookup_dict, output_column_name="Updated Column"):
        """
        This function updates values in a specified column of the DataFrame based on a lookup dictionary.
        It first merges several columns into a new 'Merged' column, then uses this merged column to determine
        if replacements are needed based on the dictionary.

        Parameters:
        df (pd.DataFrame): The DataFrame to process.
        col (str): The name of the column whose values are potentially replaced.
        replacement_rows (str): The specific value in 'col' to check for replacements.
        cols_to_merge (list of str): List of column names whose contents will be merged to form a lookup key.
        replacement_lookup_dict (dict): Dictionary where keys are merged column values and values are the new data to replace in 'col'.
        output_column_name (str, optional): Name of column outputted. Defaults to "Updated Column".

        Returns:
        pd.DataFrame: The modified DataFrame with updated values in the specified column.
        """
        # Create a merged column from specified columns
        df["Merged"] = df[cols_to_merge].apply(lambda row: '|'.join(row.values.astype(str)), axis=1)
        
        # Replace values in the specified column based on the lookup
        def replace_values(x):
            if x[col] == replacement_rows:
                merged_value = x['Merged']  
                if merged_value in replacement_lookup_dict:
                    return replacement_lookup_dict[merged_value]
            return x[col]
        
        # Apply replacement logic
        df[output_column_name] = df.apply(replace_values, axis=1)
        
        # Drop the intermediate 'Merged' column
        df.drop(columns=['Merged'], inplace=True)
        
        return df

    def create_new_version_of_col_using_LUT(self, df, keys_col,value_col, dict_for_specific_changes, new_col_name="New Version of Old Col"):
        """
        Creates a new column in a dataframe, which takes an old column and uses a lookup table to changes values in the new column to reflect the lookup table. 
        The lookup is based on a column in the dataframe. Can only input one column and output one new column.

        Parameters:
            df (pandas.DataFrame): The DataFrame containing the data.
            keys_col (str): The name of the column which the LUT will be refercing to ouput a value.
            value_col (str): The name of the column which the new column will be based off. If a key in the key column is not found in the LUT, the values from this column are used instead.
            dict_for_specific_changes (dict): The LUT which the keys_col will be mapped on to find any values that need changing in the new column.
            new_col_name (str, optional): This is the name of the new column being generated. Defaults to "New Version of Old Col".

        Returns:
        pandas.DataFrame: DataFrame with a new column which is similar to the old column, except for where changes have been made to reflect the lookup table.
        """
    
        # Extract columns to change using new dictionary
        smaller_df = df[[keys_col,value_col]]

        # Use the new dictionary to create a new LUT
        smaller_df_with_LUT = self.apply_lookup_table_for_columns(smaller_df,[keys_col,value_col],dict_for_specific_changes)
        
        # In a new column, keep values from the old column that don't need updating as they are not in the dictionary, and replace values that do need updating with values from the dictionary based on the keys
        smaller_df_with_LUT["Updated Col"]=smaller_df_with_LUT.apply(lambda x: x['Mapping'] if x['Mapping'] != "Other" else x[value_col],axis=1)

        # Drop the extra unecessary cols
        smaller_df_with_LUT.drop([keys_col,'Mapping'],axis=1,inplace=True)
        
        # # Output dataframes as dictionary to be used in a LUT
        new_dict = self.convert_2_df_cols_to_dict(smaller_df_with_LUT,value_col,"Updated Col")

        # # Use new dictionary to create a new version of an old column
        df_final = self.apply_lookup_table_for_columns(df,[keys_col],new_dict,"other",new_col_name)
        
        return df_final
    
    def convert_df_wide_2_long(self, df, value_cols, variable_col_name='Stacked', value_col_name='Value'):
        """
        Changes a dataframe from wide to long format.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            value_cols (list of str or str if only one): List of column names to transform from several columns into one.
            variable_col_name (str, optional): Name of the new variable column containing the original column names. Defaults to 'Stacked'.
            value_col_name (str, optional): Name of the new value column containing the data from stacked columns. Defaults to 'Value'.

        Returns:
            pandas.DataFrame: DataFrame transformed from wide to long format.

        Raises:
            ValueError: If the number of columns to depivot is less than 2.
        """
        # Check length of value_cols is greater than 1
        if len(value_cols) < 2:
            raise ValueError("Number of inputs in list must be greater than 1")

        # Find the columns that are not to be depivoted into one column
        id_vars = [col for col in df.columns if col not in value_cols]  # Preserve column order in the DataFrame

        # Melt all columns chosen into one column
        df_final = pd.melt(df, id_vars=id_vars, value_vars=value_cols, var_name=variable_col_name, value_name=value_col_name)

        # Sort column order to match expected output
        ordered_columns = id_vars + [variable_col_name, value_col_name]
        df_final = df_final[ordered_columns]

        return df_final

    def manually_edit_data(self, df, filters_dict, col_to_change, new_value, change_in_existing_df_col="No", new_col_to_change_name='New', manual_edit_col_name=None, add_notes="No", existing_note_col_name=None, note=None):
        """
        Allows the capability to manually update any cell in dataframe by applying filters and chosing a column to edit in dataframe

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            filters_dict (dict): Dictionary of conditions for the boolean mask i.e. what to filter your df on to get to your chosen cell
            col_to_change (str): String name of column to edit
            new_value (any): Value of new input for cell
            change_in_existing_df_col (str, optional): Input of Yes or No to describe whether to make the change in an existing column. Defaults to "No".
            new_col_to_change_name (str, optional): Name of the new column to copy the column being edited into and to make the change in. Defaults to 'New'.
            manual_edit_col_name (str, optional): Name of the current manual edits column, if one is not specified it will be created. Defaults to None.
            add_notes (str, optional): Gives the option to create a new notes column. Defaults to "No".
            existing_note_col_name (str, optional): If there is an existing notes column this can be specified. Defaults to None.
            note (str), optional): The string of the note to be added to the column. Defaults to None.

        Raises:
            TypeError: The column for the column to change can only be specified as one column as it is a string not a list
            ValueError: You can only input the values of "Yes" or "No" for whether to make the change in existing column
            ValueError: You can only input the values of "Yes" or "No" for whether to make a new notes column

        Returns:
            pandas.DataFrame: Dataframe with manual changes added
        """
 
        # Raise type error if more than one col is supported
        if isinstance(col_to_change, list):
            raise TypeError("Col to change must be specified as a string, not a list")

        # Raises value error if input is invalid for change_in_existing_df_col
        if change_in_existing_df_col not in ["Yes", "No"]:
            raise ValueError("Invalid input value for change_in_existing_df_col. Allowed values are: ['Yes', 'No']")

        # Raises value error if input is invalid for add_notes_col
        if add_notes not in ["Yes", "No"]:
            raise ValueError("Invalid input value for add_notes. Allowed values are: ['Yes', 'No']")

        # Validate filters_dict format
        for col, cond in filters_dict.items():
            if not isinstance(cond, str) or len(cond.split(maxsplit=1)) < 2:
                raise ValueError(f"Invalid filter condition for column '{col}': '{cond}'. Expected format: 'operator value'")

        # Create the filtered df by applying the conditions
        df_filtered = self.filter_df_on_multiple_conditions(df, filters_dict)

        # Create a new column to add the changes if desired, else edit in the current chosen column
        col_to_update = col_to_change if change_in_existing_df_col == "Yes" else new_col_to_change_name
        if change_in_existing_df_col == "No" and new_col_to_change_name not in df.columns:
            df = df.copy()
            df[new_col_to_change_name] = df[col_to_change]

        # Update the new cell in the chosen column
        df.loc[df_filtered.index, col_to_update] = new_value

        # Add in manual edit column if desired or specify where one already is
        if manual_edit_col_name:
            if manual_edit_col_name not in df.columns:
                df[manual_edit_col_name] = 0
            df.loc[df_filtered.index, manual_edit_col_name] = 1
        elif not manual_edit_col_name and 'Manual Changes' not in df.columns:
            df['Manual Changes'] = 0
            df.loc[df_filtered.index, 'Manual Changes'] = 1

        # Add note if desired in new column or an existing column
        if add_notes == "Yes":
            note_col = existing_note_col_name if existing_note_col_name else 'Notes'
            if note_col not in df.columns:
                df[note_col] = None
            df.loc[df_filtered.index, note_col] = note

        return df
    
    def format_numbers_with_commas(self, df, decimal_length_chosen=2):
        """
        Converts data in numerical format into numbers with commas and a chosen decimal place length.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            decimal_length_chosen (int, optional): Number of decimal places. Defaults to 2.

        Returns:
            pandas.DataFrame: The DataFrame with the chosen updated format.
        """
        def format_number_with_commas(x, decimal_length=decimal_length_chosen):
            if pd.isna(x):  # Preserve None/NaN values
                return pd.NA  # Explicitly normalize to pd.NA
            elif isinstance(x, (int, float)):
                if decimal_length is not None:
                    format_str = f"{{:,.{decimal_length}f}}"
                    return format_str.format(x)
                else:
                    return f"{x:,}"
            else:
                return x  # Return unchanged if not a number

        # Apply formatting column by column
        formatted_df = df.apply(lambda col: col.map(format_number_with_commas)).fillna(value=pd.NA)

        return formatted_df
        
    def filter_df_on_multiple_conditions(self, df, filters_dict):
        """
        Filter a dataframe based on mulitple conditions

        Args:
            df (pandas.DatFrame): Dataframe to filter on
            filters_dict (dict): Dictionary with strings as conditions

        Returns:
            pandas.DatFrame: Filtered Da
        """
        mask = pd.Series(True, index=df.index)
        for col, cond in filters_dict.items():
            cond = cond.strip()
            operator, value = cond.split(maxsplit=1)
            
            # If value is a string condition make sure to check if there are new lines
            if "'" in value:
                value = value.strip().strip("'\"")
            # If not a string e.g. datetime or number condition you need to transform the string into a value
            else:
                value = eval(value)  

            if operator == "==":
                temp_mask = (df[col] == value)
            elif operator == "!=":
                temp_mask = (df[col] != value)
            elif operator == ">=":
                temp_mask = (df[col] >= value)
            elif operator == "<=":
                temp_mask = (df[col] <= value)
            elif operator == ">":
                temp_mask = (df[col] > value)
            elif operator == "<":
                temp_mask = (df[col] < value)                          
            mask &= temp_mask

        # Create the filtered df by applying the conditions
        df_filtered = df[mask]
    
        return df_filtered
    
    def read_and_concatenate_files(self, folder_path, file_type='csv'):
        """
        Reads all files of a specified type (CSV or XLSX) from a given folder 
        and concatenates them into a single DataFrame.
        
        Parameters:
        folder_path (str): The path to the folder containing the files.
        file_type (str): The type of files to read ('csv' or 'xlsx'). Defaults to 'csv'.
        
        Returns:
        pd.DataFrame: A DataFrame containing the concatenated data from all files.
        """
        
        # Initialize an empty list to hold dataframes
        dataframes = []

        # Define file extension based on file_type
        if file_type == 'csv':
            extension = '.csv'
        elif file_type == 'xlsx':
            extension = '.xlsx'
        else:
            raise ValueError("file_type must be either 'csv' or 'xlsx'")

        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            # Check if the file has the correct extension
            if filename.endswith(extension):
                file_path = os.path.join(folder_path, filename)
                # Read the file into a DataFrame
                if file_type == 'csv':
                    df = pd.read_csv(file_path)
                elif file_type == 'xlsx':
                    df = pd.read_excel(file_path)
                # Append the DataFrame to the list
                dataframes.append(df)

        # Concatenate all DataFrames into a single DataFrame
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        return combined_df
    
    def upgrade_outdated_packages(self, exclude_packages=['twine']):
        """
        Upgrade all outdated Python packages except those specified in `exclude_packages`.

        :param exclude_packages: List of package names to exclude from the upgrade process.
        """
        exclude_packages = set(exclude_packages or [])

        try:
            # Get all installed packages
            installed_packages_result = subprocess.run(
                "pip list --format=json", shell=True, capture_output=True, text=True
            )
            installed_packages = json.loads(installed_packages_result.stdout)

            # Get the list of outdated packages
            outdated_packages_result = subprocess.run(
                "pip list --outdated --format=json", shell=True, capture_output=True, text=True
            )
            outdated_packages = json.loads(outdated_packages_result.stdout)

            # Create a set of outdated package names for quick lookup
            outdated_package_names = {pkg['name'] for pkg in outdated_packages}

            # Upgrade only outdated packages, excluding specified packages
            for package in installed_packages:
                package_name = package['name']
                if package_name in outdated_package_names and package_name not in exclude_packages:
                    try:
                        print(f"Upgrading package: {package_name}")
                        upgrade_result = subprocess.run(
                            f"pip install --upgrade {package_name}", shell=True, capture_output=True, text=True
                        )
                        if upgrade_result.returncode == 0:
                            print(f"Successfully upgraded {package_name}")
                        else:
                            print(f"Failed to upgrade {package_name}: {upgrade_result.stderr}")
                    except Exception as e:
                        print(f"An error occurred while upgrading {package_name}: {e}")
                elif package_name in exclude_packages:
                    print(f"Skipping package: {package_name} (excluded)")
                else:
                    print(f"{package_name} is already up to date or not outdated")
        except Exception as e:
            print(f"An error occurred during the upgrade process: {e}")

    def convert_mixed_formats_dates(self, df, column_name):
        # Convert initial dates to datetime with coercion to handle errors
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
        df[column_name] = df[column_name].astype(str)
        corrected_dates = []
        
        for date_str in df[column_name]:
            date_str = date_str.replace('-', '').replace('/', '')
            if len(date_str) == 8:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                if int(day) <= 12:
                    # Swap month and day
                    corrected_date_str = f"{year}-{day}-{month}"
                else:
                    corrected_date_str = f"{year}-{month}-{day}"
                # Convert to datetime
                corrected_date = pd.to_datetime(corrected_date_str, errors='coerce')
            else:
                corrected_date = pd.to_datetime(date_str, errors='coerce')
            
            corrected_dates.append(corrected_date)
        
        # Check length of the corrected_dates list
        if len(corrected_dates) != len(df):
            raise ValueError("Length of corrected_dates does not match the original DataFrame")
        
        # Assign the corrected dates back to the DataFrame
        df[column_name] = corrected_dates
        return df

    def fill_weekly_date_range(self, df, date_column, freq='W-MON'):
        # Ensure the date column is in datetime format
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Generate the full date range with the specified frequency
        full_date_range = pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=freq)
        
        # Create a new dataframe with the full date range
        full_date_df = pd.DataFrame({date_column: full_date_range})
        
        # Merge the original dataframe with the new full date range dataframe
        df_full = full_date_df.merge(df, on=date_column, how='left')
        
        # Fill missing values with 0
        df_full.fillna(0, inplace=True)
        
        return df_full
    
    def add_prefix_and_suffix(self, df, prefix='', suffix='', date_col=None):
        """
        Adds a specified prefix and/or suffix to the column names of a DataFrame. Optionally, a column (e.g., a date column) can be excluded.

        Args:
        df (pd.DataFrame): The DataFrame whose column names will be modified.
        prefix (str, optional): The prefix to add to each column name. Default is an empty string.
        suffix (str, optional): The suffix to add to each column name. Default is an empty string.
        date_col (str, optional): The name of the column to exclude from adding prefix and suffix, typically a date column. Default is None.

        Returns:
        pd.DataFrame: The DataFrame with updated column names.
        """
        
        # If there is no date column
        if date_col is None:
            # Add prefixes and suffixes to all columns
            df.columns = [prefix + col + suffix for col in df.columns]
        else:
            # Add prefixes and suffixes to all columns except the date column
            df.columns = [prefix + col + suffix if col != date_col else col for col in df.columns]
            
        return df

    def create_dummies(self, df, date_col=None, dummy_threshold=0, add_total_dummy_col='No', total_col_name='total'):
        """
        Creates dummy variables for the DataFrame, converting values greater than the threshold to 1 and others to 0.
        Optionally adds a total dummy column indicating whether any row contains at least one value greater than the threshold.

        Args:
        df (pd.DataFrame): The DataFrame to process.
        date_col (str, optional): The column name to exclude from the dummy conversion, typically a date column. Default is None.
        dummy_threshold (int, optional): The threshold value; values greater than this become 1, others become 0. Default is 0.
        add_total_dummy_col (str, optional): If set to any value other than 'No', adds a column that contains the max value (1 or 0) for each row. Default is 'No'.
        total_col_name (str, optional): The name of the total column to add if add_total_dummy_col is not 'No'. Default is 'total'.

        Returns:
        pd.DataFrame: The modified DataFrame with dummies applied and optional total column.
        """

        # If there is no date column
        if date_col is None:
            df = df.apply(lambda col: col.map(lambda x: 1 if x > dummy_threshold else 0))

            if add_total_dummy_col != 'No':
                # Find max value of rows
                df[total_col_name] = df.max(axis=1)

        # If there is a date column
        else:
            # Create dummies for all columns except the date column
            df.loc[:, df.columns != date_col] = df.loc[:, df.columns != date_col].apply(
                lambda col: col.map(lambda x: 1 if x > dummy_threshold else 0)
            )

            if add_total_dummy_col != 'No':
                # Find max value of rows
                df[total_col_name] = df.loc[:, df.columns != date_col].max(axis=1)

        return df

    def replace_substrings(self, df, column, replacements, to_lower=False, new_column=None):
        """
        Replaces substrings in a column of a DataFrame based on a dictionary of replacements. 
        Optionally converts the column values to lowercase and allows creating a new column or modifying the existing one.

        Args:
        df (pd.DataFrame): The DataFrame containing the column to modify.
        column (str): The column name where the replacements will be made.
        replacements (dict): A dictionary where keys are substrings to replace and values are the replacement strings.
        to_lower (bool, optional): If True, the column values will be converted to lowercase before applying replacements. Default is False.
        new_column (str, optional): If provided, the replacements will be applied to this new column. If None, the existing column will be modified. Default is None.

        Returns:
        pd.DataFrame: The DataFrame with the specified replacements made, and optionally with lowercase strings.
        """
        if new_column is not None:
            # Create a new column for replacements
            df[new_column] = df[column]
            temp_column = new_column
        else:
            # Modify the existing column
            temp_column = column

        # Optionally convert to lowercase
        if to_lower:
            df[temp_column] = df[temp_column].str.lower()

        # Apply substring replacements
        for old, new in replacements.items():
            df[temp_column] = df[temp_column].str.replace(old, new, regex=False)

        return df

    def add_total_column(self, df, exclude_col=None, total_col_name='Total'):
        """
        Adds a total column to a DataFrame by summing across all columns. Optionally excludes a specified column.

        Args:
        df (pd.DataFrame): The DataFrame to modify.
        exclude_col (str, optional): The column name to exclude from the sum. Default is None.
        total_col_name (str, optional): The name of the new total column. Default is 'Total'.

        Returns:
        pd.DataFrame: The DataFrame with an added total column.
        """
        if exclude_col and exclude_col in df.columns:
            # Ensure the column to exclude exists before dropping
            df[total_col_name] = df.drop(columns=[exclude_col], errors='ignore').sum(axis=1)
        else:
            # Sum across all columns if no column is specified to exclude
            df[total_col_name] = df.sum(axis=1)
        
        return df

    def apply_lookup_table_based_on_substring(self, df, column_name, category_dict, new_col_name='Category', other_label='Other'):
        """
        Categorizes text in a specified DataFrame column by applying a lookup table based on substrings.

        Args:
        df (pd.DataFrame): The DataFrame containing the column to categorize.
        column_name (str): The name of the column in the DataFrame that contains the text data to categorize.
        category_dict (dict): A dictionary where keys are substrings to search for in the text and values are the categories to assign when a substring is found.
        new_col_name (str, optional): The name of the new column to be created in the DataFrame, which will hold the resulting categories. Default is 'Category'.
        other_label (str, optional): The name given to category if no substring from the dictionary is found in the cell

        Returns:
        pd.DataFrame: The original DataFrame with an additional column containing the assigned categories.
        """

        def categorize_text(text):
            """
            Assigns a category to a single text string based on the presence of substrings from a dictionary.

            Args:
            text (str): The text string to categorize.

            Returns:
            str: The category assigned based on the first matching substring found in the text. If no 
            matching substring is found, returns other_name.
            """
            for key, category in category_dict.items():
                if key.lower() in text.lower():  # Check if the substring is in the text (case-insensitive)
                    return category
            return other_label  # Default category if no match is found

        # Apply the categorize_text function to each element in the specified column
        df[new_col_name] = df[column_name].apply(categorize_text)
        return df

    def compare_overlap(self, df1, df2, date_col):
        """
        Compare overlapping periods between two DataFrames and provide a summary of total differences.

        Args:
            df1 (pandas.DataFrame): First DataFrame containing date-based data.
            df2 (pandas.DataFrame): Second DataFrame containing date-based data.
            date_col (str): The name of the date column used for aligning data.

        Returns:
            tuple: A tuple containing the DataFrame of differences and a summary DataFrame with total differences by column.
        """
        # Ensure date columns are in datetime format
        df1[date_col] = pd.to_datetime(df1[date_col])
        df2[date_col] = pd.to_datetime(df2[date_col])

        # Determine the overlap period
        start_date = max(df1[date_col].min(), df2[date_col].min())
        end_date = min(df1[date_col].max(), df2[date_col].max())

        # Filter DataFrames to the overlapping period
        df1_overlap = df1[(df1[date_col] >= start_date) & (df1[date_col] <= end_date)]
        df2_overlap = df2[(df2[date_col] >= start_date) & (df2[date_col] <= end_date)]

        # Merge the DataFrames on the date column
        merged_df = pd.merge(df1_overlap, df2_overlap, on=date_col, suffixes=('_df1', '_df2'))

        # Get common columns, excluding the date column
        common_cols = [col for col in df1.columns if col != date_col and col in df2.columns]

        # Create a DataFrame for differences
        diff_df = pd.DataFrame({date_col: merged_df[date_col]})

        total_diff_list = []
        for col in common_cols:
            diff_col = f'diff_{col}'
            diff_df[diff_col] = merged_df[f'{col}_df1'] - merged_df[f'{col}_df2']  # Corrected subtraction order

            # Sum differences for the column
            total_diff = diff_df[diff_col].sum()
            total_diff_list.append({'Column': col, 'Total Difference': total_diff})

        # Create summary DataFrame
        total_diff_df = pd.DataFrame(total_diff_list)

        return diff_df, total_diff_df

    def week_commencing_2_week_commencing_conversion_isoweekday(self, df, date_col, week_commencing='mon'):
        """
        Convert a DataFrame's date column so that each date is mapped back
        to the 'week_commencing' day of the *current ISO week*.

        Args:
            df (pandas.DataFrame): The DataFrame with date-based data.
            date_col (str): The name of the date column.
            week_commencing (str): The desired start of the week. 
                ('mon'=Monday, 'tue'=Tuesday, ..., 'sun'=Sunday).
                Uses ISO day numbering (Mon=1, ..., Sun=7).

        Returns:
            pandas.DataFrame: Original DataFrame with an extra column
                            'week_start_<week_commencing>' containing the
                            start-of-week date for each row.
        """
        # ISO-based dictionary: Monday=1, Tuesday=2, ..., Sunday=7
        iso_day_dict = {"mon": 1, "tue": 2, "wed": 3, "thur": 4, "fri": 5, "sat": 6, "sun": 7}

        target_day = iso_day_dict[week_commencing]

        def map_to_week_start(date_val):
            delta = (date_val.isoweekday() - target_day) % 7
            return date_val - pd.Timedelta(days=delta)

        # Apply the transformation
        new_col = f"week_start_{week_commencing}"
        df[new_col] = df[date_col].apply(map_to_week_start)
        
        return df
    
    def seasonality_feature_extraction(self, df, kpi_var, n_features=10, test_size=0.1, random_state=42, shuffle=False):
        """
        1) Uses the provided dataframe (df), where:
        - df['kpi_total_sales'] is the target (y).
        - df['OBS'] is a date or index column (excluded from features).
        
        2) Splits data into train/test using the specified test_size, random_state, and shuffle.
        3) Trains XGBoost and Random Forest on all features.
        4) Extracts the top n_features from each model.
        5) Merges their unique top features.
        6) Optionally retrains each model on the combined top features.
        7) Returns performance metrics and the fitted models.

        Parameters
        ----------
        df : pd.DataFrame
            The input dataframe that contains kpi_var (target) and 'OBS' (date/index).
        n_features : int, optional
            Number of top features to extract from each model (default=10).
        test_size : float, optional
            Test size for train_test_split (default=0.1).
        random_state : int, optional
            Random state for reproducibility (default=42).
        shuffle : bool, optional
            Whether to shuffle the data before splitting (default=False).

        Returns
        -------
        dict
            A dictionary containing:
            - "top_features_xgb": list of top n_features from XGBoost
            - "top_features_rf": list of top n_features from Random Forest
            - "combined_features": merged unique feature list
            - "performance": dictionary of performance metrics
            - "models": dictionary of fitted models
        """
        # ---------------------------------------------------------------------
        # 1. Prepare your data (X, y)
        # ---------------------------------------------------------------------
        # Extract target and features
        y = df[kpi_var]
        X = df.drop(columns=['OBS', kpi_var])

        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            shuffle=shuffle
        )

        # ---------------------------------------------------------------------
        # 2. XGBoost Approach (on all features)
        # ---------------------------------------------------------------------
        # (A) Train full model on ALL features
        xgb_model_full = xgb.XGBRegressor(random_state=random_state)
        xgb_model_full.fit(X_train, y_train)

        # (B) Get feature importances
        xgb_importances = xgb_model_full.feature_importances_
        xgb_feat_importance_df = (
            pd.DataFrame({
                'feature': X.columns,
                'importance': xgb_importances
            })
            .sort_values('importance', ascending=False)
            .reset_index(drop=True)
        )

        # (C) Select top N features
        top_features_xgb = xgb_feat_importance_df['feature'].head(n_features).tolist()

        # (D) Subset data to top N features
        X_train_xgb_topN = X_train[top_features_xgb]

        # (E) Retrain XGBoost on these top N features
        xgb_model_topN = xgb.XGBRegressor(random_state=random_state)
        xgb_model_topN.fit(X_train_xgb_topN, y_train)

        # ---------------------------------------------------------------------
        # 3. Random Forest Approach (on all features)
        # ---------------------------------------------------------------------
        rf_model_full = RandomForestRegressor(random_state=random_state)
        rf_model_full.fit(X_train, y_train)

        # (B) Get feature importances
        rf_importances = rf_model_full.feature_importances_
        rf_feat_importance_df = (
            pd.DataFrame({
                'feature': X.columns,
                'importance': rf_importances
            })
            .sort_values('importance', ascending=False)
            .reset_index(drop=True)
        )

        # (C) Select top N features
        top_features_rf = rf_feat_importance_df['feature'].head(n_features).tolist()

        # (D) Subset data to top N features
        X_train_rf_topN = X_train[top_features_rf]

        # (E) Retrain Random Forest on these top N features
        rf_model_topN = RandomForestRegressor(random_state=random_state)
        rf_model_topN.fit(X_train_rf_topN, y_train)

        # ---------------------------------------------------------------------
        # 4. Combine top features from both models
        # ---------------------------------------------------------------------
        combined_features = list(set(top_features_xgb + top_features_rf))

        # Create new training/testing data with the combined features
        X_train_combined = X_train[combined_features]

        # (Optional) Retrain XGBoost on combined features
        xgb_model_combined = xgb.XGBRegressor(random_state=random_state)
        xgb_model_combined.fit(X_train_combined, y_train)

        # (Optional) Retrain Random Forest on combined features
        rf_model_combined = RandomForestRegressor(random_state=random_state)
        rf_model_combined.fit(X_train_combined, y_train)

        # Organize all results to return
        output = {
            "combined_features": combined_features,
        }

        return output

    def quid_pr (self, df):
        def convert_date(date_str):
            try:
                return datetime.strptime(date_str, '%b %d, %Y')
            except ValueError:
                return None  # Return None if conversion fails
        # Apply conversion to create new columns
        df['Start Date'] = df['Earliest Published'].astype(str).apply(convert_date)
        df['End Date'] = df['Latest Published'].astype(str).apply(convert_date)
        df['Days Duration'] = (df['End Date'] - df['Start Date']).dt.days + 1  # Ensure inclusive range
        df['Count per Day'] = df['Published Count'] / df['Days Duration'] # Calculate count per day
        df['Social Engagement per Day'] = df['Social Engagement'] / df['Days Duration']
        df['Week Start'] = df['Start Date'].apply(lambda x: x - timedelta(days=x.weekday()) if pd.notnull(x) else None)
        count_df = df.groupby('Week Start')['Count per Day'].sum().reset_index()
        total_engagement_per_company = df.groupby('Company (Primary Mention)')['Social Engagement'].sum().reset_index() # Caluclates Social Engagement across whole period
        valid_companies = total_engagement_per_company[total_engagement_per_company['Social Engagement'] > 0]['Company (Primary Mention)'] # Filters out Companies with no Social Engagement
        social_engagement_df = df[df['Company (Primary Mention)'].isin(valid_companies)].groupby(['Week Start', 'Company (Primary Mention)'])[
        'Social Engagement'
        ].sum().reset_index()
        total_social_engagement_df = df.groupby('Week Start')['Social Engagement per Day'].sum().reset_index()
        
        return count_df, total_social_engagement_df, social_engagement_df