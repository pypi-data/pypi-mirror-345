import unittest
import pandas as pd
import numpy as np
import os
from mmm import dataprocessing

class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.dp = dataprocessing()
        self.df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
            'value1': range(10),
            'value2': range(10, 20)
        })
        self.mixed_date_df = pd.DataFrame({
            'mixed_date': ['2023-01-01', '01/02/2023', '2023/03/01', '2023-04-01']
        })
        self.merged_df = pd.DataFrame({
            'col1': ["A", "B", "C"],
            'col2': ["X", "Y", "Z"]
        })

    def test_get_wd_levels(self):
        current_dir = os.getcwd()
        parent_dir = self.dp.get_wd_levels(1)
        self.assertEqual(parent_dir, os.path.dirname(current_dir))

    def test_aggregate_daily_to_wc_long(self):
        # Create a test DataFrame
        test_data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-08', '2023-01-09', '2023-01-10'],
            'group_col': ['A', 'A', 'B', 'B', 'B'],
            'value1': [10, 20, 30, 40, np.nan],
            'value2': [100, 200, 300, np.nan, 500]
        }
        df = pd.DataFrame(test_data)

        # Expected output for different test cases
        expected_sum_output = pd.DataFrame({
            'OBS': ['2023-01-01', '2023-01-08'],  # Week starting on Sunday
            'group_col': ['A', 'B'],
            'value1': [30.0, 70.0],
            'value2': [300.0, 800.0]
        })

        # Convert OBS column to datetime for expected DataFrame
        expected_sum_output['OBS'] = pd.to_datetime(expected_sum_output['OBS'])

        # Test sum aggregation
        result_sum = self.dp.aggregate_daily_to_wc_long(df, 'date', ['group_col'], ['value1', 'value2'], wc='sun', aggregation='sum')

        # Ensure both OBS columns are datetime for comparison
        result_sum['OBS'] = pd.to_datetime(result_sum['OBS'])

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result_sum, expected_sum_output)
        
    def test_convert_monthly_to_daily(self):
        # Create a test DataFrame with monthly data
        test_data = {
            'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'value1': [31, 28, 31],
            'value2': [310, 280, 310]
        }
        df = pd.DataFrame(test_data)

        # Expected output DataFrame when divide=True
        expected_daily_data_divide = {
            'date': pd.date_range(start='2023-01-01', end='2023-01-31').tolist() +
                    pd.date_range(start='2023-02-01', end='2023-02-28').tolist() +
                    pd.date_range(start='2023-03-01', end='2023-03-31').tolist(),
            'value1': [1.0] * 31 + [1.0] * 28 + [1.0] * 31,
            'value2': [10.0] * 31 + [10.0] * 28 + [10.0] * 31
        }
        expected_daily_df_divide = pd.DataFrame(expected_daily_data_divide)

        # Call the function with divide=True
        result_divide = self.dp.convert_monthly_to_daily(df, 'date', divide=True)

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result_divide.reset_index(drop=True), expected_daily_df_divide)

        # Expected output DataFrame when divide=False
        expected_daily_data_no_divide = {
            'date': pd.date_range(start='2023-01-01', end='2023-01-31').tolist() +
                    pd.date_range(start='2023-02-01', end='2023-02-28').tolist() +
                    pd.date_range(start='2023-03-01', end='2023-03-31').tolist(),
            'value1': [31] * 31 + [28] * 28 + [31] * 31,
            'value2': [310] * 31 + [280] * 28 + [310] * 31
        }
        expected_daily_df_no_divide = pd.DataFrame(expected_daily_data_no_divide)

        # Call the function with divide=False
        result_no_divide = self.dp.convert_monthly_to_daily(df, 'date', divide=False)

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result_no_divide.reset_index(drop=True), expected_daily_df_no_divide)

    def test_week_of_year_mapping(self):
        # Create a test DataFrame with ISO week format
        test_data = {
            'week_col': ['2023-W01', '2023-W05', '2023-W10', '2023-W52']
        }
        df = pd.DataFrame(test_data)

        # Expected outputs for different start days
        expected_output_mon = pd.DataFrame({
            'week_col': ['2023-W01', '2023-W05', '2023-W10', '2023-W52'],
            'OBS': ['02/01/2023', '30/01/2023', '06/03/2023', '25/12/2023']
        })

        expected_output_sun = pd.DataFrame({
            'week_col': ['2023-W01', '2023-W05', '2023-W10', '2023-W52'],
            'OBS': ['01/01/2023', '29/01/2023', '05/03/2023', '24/12/2023']
        })

        # Test mapping with Monday as start day
        result_mon = self.dp.week_of_year_mapping(df.copy(), 'week_col', 'mon')
        pd.testing.assert_frame_equal(result_mon, expected_output_mon)

        # Test mapping with Sunday as start day
        result_sun = self.dp.week_of_year_mapping(df.copy(), 'week_col', 'sun')
        pd.testing.assert_frame_equal(result_sun, expected_output_sun)

        # Test with invalid start day input
        with self.assertRaises(ValueError) as context:
            self.dp.week_of_year_mapping(df.copy(), 'week_col', 'invalid_day')
        self.assertIn("Invalid day input", str(context.exception))

    def test_rename_cols(self):
        # Create a test DataFrame
        test_data = {
            'OBS': [1, 2, 3],
            'Column One': [10, 20, 30],
            'Another Column': [100, 200, 300],
            'Special Characters !@#': [5, 15, 25]
        }
        df = pd.DataFrame(test_data)

        # Expected output with default prefix
        expected_output_default = pd.DataFrame({
            'OBS': [1, 2, 3],
            'ame_column_one': [10, 20, 30],
            'ame_another_column': [100, 200, 300],
            'ame_special_characters_!@#': [5, 15, 25]
        })

        # Expected output with custom prefix
        expected_output_custom = pd.DataFrame({
            'OBS': [1, 2, 3],
            'custom_column_one': [10, 20, 30],
            'custom_another_column': [100, 200, 300],
            'custom_special_characters_!@#': [5, 15, 25]
        })

        # Test renaming columns with default prefix
        result_default = self.dp.rename_cols(df)
        pd.testing.assert_frame_equal(result_default, expected_output_default)

        # Test renaming columns with custom prefix
        result_custom = self.dp.rename_cols(df, name='custom_')
        pd.testing.assert_frame_equal(result_custom, expected_output_custom)

        # Test that 'OBS' column remains unchanged
        self.assertIn('OBS', result_default.columns)
        self.assertIn('OBS', result_custom.columns)

    def test_merge_new_and_old(self):
        # Create test DataFrames for old and new data
        old_data = {
            'OBS': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
            'old_values': [10, 20, 30, 40]
        }
        new_data = {
            'OBS': ['2023-01-04', '2023-01-05', '2023-01-06'],
            'new_values': [100, 200, 300]
        }
        old_df = pd.DataFrame(old_data)
        new_df = pd.DataFrame(new_data)

        # Expected output
        expected_output = pd.DataFrame({
            'OBS': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06']),
            'new_values': [10, 20, 30, 40, 200, 300]
        })

        # Test merging with cutoff_date='2023-01-04'
        result = self.dp.merge_new_and_old(old_df, 'old_values', new_df, 'new_values', '2023-01-04')

        # Assertions
        pd.testing.assert_frame_equal(result, expected_output)

        # Test that columns are correctly renamed and sorted
        self.assertIn('OBS', result.columns)
        self.assertIn('new_values', result.columns)
        self.assertEqual(len(result), len(expected_output))  # Ensure row count matches
        self.assertTrue((result['OBS'].diff().dropna() >= pd.Timedelta(0)).all())  # Check that dates are in order

    def test_merge_dataframes_on_column(self):
        # Create test DataFrames
        df1 = pd.DataFrame({
            'OBS': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'value1': [10, 20, 30]
        })
        df2 = pd.DataFrame({
            'OBS': ['2023-01-02', '2023-01-03', '2023-01-04'],
            'value2': [40, 50, 60]
        })
        df3 = pd.DataFrame({
            'OBS': ['2023-01-03', '2023-01-04', '2023-01-05'],
            'value3': [70, 80, 90]
        })

        # Ensure test DataFrame columns are datetime
        df1['OBS'] = pd.to_datetime(df1['OBS'])
        df2['OBS'] = pd.to_datetime(df2['OBS'])
        df3['OBS'] = pd.to_datetime(df3['OBS'])

        # Expected output for outer merge (cast to float64 to match the behavior of fillna)
        expected_output_outer = pd.DataFrame({
            'OBS': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
            'value1': [10.0, 20.0, 30.0, 0.0, 0.0],
            'value2': [0.0, 40.0, 50.0, 60.0, 0.0],
            'value3': [0.0, 0.0, 70.0, 80.0, 90.0]
        })

        # Expected output for inner merge
        expected_output_inner = pd.DataFrame({
            'OBS': pd.to_datetime(['2023-01-03']),
            'value1': [30],
            'value2': [50],
            'value3': [70]
        })

        # Test outer merge
        result_outer = self.dp.merge_dataframes_on_column([df1, df2, df3], common_column='OBS', merge_how='outer')
        pd.testing.assert_frame_equal(result_outer.reset_index(drop=True), expected_output_outer)

        # Test inner merge
        result_inner = self.dp.merge_dataframes_on_column([df1, df2, df3], common_column='OBS', merge_how='inner')
        pd.testing.assert_frame_equal(result_inner.reset_index(drop=True), expected_output_inner)

        # Test with empty DataFrame list
        result_empty = self.dp.merge_dataframes_on_column([], common_column='OBS', merge_how='outer')
        self.assertIsNone(result_empty)

        # Test with one DataFrame in the list
        result_single = self.dp.merge_dataframes_on_column([df1], common_column='OBS', merge_how='outer')
        pd.testing.assert_frame_equal(result_single.reset_index(drop=True), df1)

        # Test that the common column is sorted and converted to datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result_outer['OBS']))
        self.assertTrue((result_outer['OBS'].diff().dropna() >= pd.Timedelta(0)).all())  # Check sorted dates

    def test_merge_and_update_dfs(self):
        # Create test DataFrames
        df1 = pd.DataFrame({
            'OBS': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'value1': [10, 20, 30],
            'value2': [100, 200, 300]
        })

        df2 = pd.DataFrame({
            'OBS': ['2023-01-02', '2023-01-03', '2023-01-04'],
            'value1': [15, 25, 35],  # Updates for value1
            'value3': [400, 500, 600]  # New column
        })

        # Ensure test DataFrame columns are datetime
        df1['OBS'] = pd.to_datetime(df1['OBS'])
        df2['OBS'] = pd.to_datetime(df2['OBS'])

        # Expected output with float64 for numeric columns
        expected_output = pd.DataFrame({
            'OBS': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04']),
            'value1': [10.0, 15.0, 25.0, 35.0],  # Updated where applicable
            'value2': [100.0, 200.0, 300.0, 0.0],  # From df1, 0 where not available
            'value3': [0.0, 400.0, 500.0, 600.0]  # From df2, 0 where not available
        })

        # Test the merge and update function
        result = self.dp.merge_and_update_dfs(df1, df2, key_column='OBS')

        # Assertions
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_output)

        # Test column order is preserved in the result
        self.assertListEqual(list(result.columns), list(expected_output.columns))

        # Test that the OBS column is sorted
        self.assertTrue((result['OBS'].diff().dropna() >= pd.Timedelta(0)).all())

    def test_convert_us_to_uk_dates(self):
        # Create a test DataFrame
        test_data = {
            'date_col': ['01-02-2023', '03/04/2023', '05-06-2023', '07/08/2023']
        }
        df = pd.DataFrame(test_data)

        # Expected output
        expected_output = pd.DataFrame({
            'date_col': pd.to_datetime(['2023-01-02', '2023-03-04', '2023-05-06', '2023-07-08'])
        })

        # Test the conversion function
        result = self.dp.convert_us_to_uk_dates(df.copy(), 'date_col')

        # Assertions
        pd.testing.assert_frame_equal(result, expected_output)

        # Test invalid input formats
        invalid_data = pd.DataFrame({'date_col': ['invalid-date', '12345']})
        with self.assertRaises(ValueError):
            self.dp.convert_us_to_uk_dates(invalid_data.copy(), 'date_col')

        # Test missing values
        missing_data = pd.DataFrame({'date_col': [None, '03/04/2023']})
        result_with_missing = self.dp.convert_us_to_uk_dates(missing_data.copy(), 'date_col')
        expected_with_missing = pd.DataFrame({
            'date_col': [pd.NaT, pd.to_datetime('2023-03-04')]
        })
        pd.testing.assert_frame_equal(result_with_missing, expected_with_missing)

    def test_pivot_table(self):
        # Create a test DataFrame
        test_data = {
            'date': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03'],
            'category': ['A', 'B', 'A', 'B', 'A'],
            'value': [10.0, 20.0, 30.0, 40.0, 50.0]
        }
        df = pd.DataFrame(test_data)

        # Ensure the 'date' column is in datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Expected output for basic pivot table
        expected_output_basic = pd.DataFrame({
            'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'A': [10.0, 30.0, 50.0],  # Cast to float64
            'B': [20.0, 40.0, 0.0]    # Cast to float64
        })
        expected_output_basic.columns.name = 'category'

        # Test basic pivot table
        result_basic = self.dp.pivot_table(df.copy(), index_col='date', columns='category', values_col='value', margins=False, fill_value=0)

        # Convert 'date' columns in both DataFrames to datetime for comparison
        result_basic['date'] = pd.to_datetime(result_basic['date'])
        expected_output_basic['date'] = pd.to_datetime(expected_output_basic['date'])
        pd.testing.assert_frame_equal(result_basic, expected_output_basic)

        # Expected output for pivot table with margins
        expected_output_with_margins = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', 'Total'],
            'A': [10.0, 30.0, 50.0, 90.0],
            'B': [20.0, 40.0, 0.0, 60.0],
            'Total': [30.0, 70.0, 50.0, 150.0]
        })
        expected_output_with_margins['date'] = pd.to_datetime(
            expected_output_with_margins['date'], errors='coerce'
        ).fillna('Total')
        expected_output_with_margins.columns.name = 'category'

        # Test pivot table with margins
        result_with_margins = self.dp.pivot_table(df.copy(), index_col='date', columns='category', values_col='value', margins=True, fill_value=0)
        result_with_margins['date'] = pd.to_datetime(result_with_margins['date'], errors='coerce').fillna('Total')
        pd.testing.assert_frame_equal(result_with_margins, expected_output_with_margins)

    def test_apply_lookup_table_for_columns(self):
        # Create a test DataFrame
        test_data = {
            'col1': ['apple', 'banana', 'carrot', 'date', 'eggplant'],
            'col2': ['fruit', 'fruit', 'vegetable', 'fruit', 'vegetable']
        }
        df = pd.DataFrame(test_data)

        # Lookup dictionary
        lookup_dict = {
            'apple': 'Red Fruit',
            'banana': 'Yellow Fruit',
            'carrot': 'Orange Vegetable',
            'date': 'Brown Fruit'
        }

        # Expected output with single column lookup
        expected_output_single = df.copy()
        expected_output_single['Mapping'] = ['Red Fruit', 'Yellow Fruit', 'Orange Vegetable', 'Brown Fruit', 'Other']

        # Test with a single column
        result_single = self.dp.apply_lookup_table_for_columns(df.copy(), col_names=['col1'], to_find_dict=lookup_dict)
        pd.testing.assert_frame_equal(result_single, expected_output_single)

        # Expected output with multiple column lookup
        expected_output_multiple = df.copy()
        expected_output_multiple['Mapping'] = ['Other', 'Other', 'Other', 'Brown Fruit', 'Other']

        # Update lookup dictionary to match merged keys
        lookup_dict_merged = {
            'date|fruit': 'Brown Fruit'
        }

        # Test with multiple columns
        result_multiple = self.dp.apply_lookup_table_for_columns(df.copy(), col_names=['col1', 'col2'], to_find_dict=lookup_dict_merged)
        pd.testing.assert_frame_equal(result_multiple, expected_output_multiple)

        # Test case where no match is found
        df_no_match = pd.DataFrame({'col1': ['unknown']})
        expected_no_match = df_no_match.copy()
        expected_no_match['Mapping'] = ['Other']
        result_no_match = self.dp.apply_lookup_table_for_columns(df_no_match, col_names=['col1'], to_find_dict=lookup_dict)
        pd.testing.assert_frame_equal(result_no_match, expected_no_match)

    def test_aggregate_daily_to_wc_wide(self):
        # Create a test DataFrame
        test_data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-08', '2023-01-09', '2023-01-10'],
            'group': ['A', 'A', 'B', 'B', 'B'],
            'value1': [10, 20, 30, 40, None],
            'value2': [100, 200, 300, None, 500]
        }
        df = pd.DataFrame(test_data)

        # Expected output for weekly aggregation in wide format
        expected_output = pd.DataFrame({
            'OBS': ['2023-01-01', '2023-01-08'],  # Weeks starting on Sunday
            'value1_A': [30.0, 0.0],
            'value1_B': [0.0, 70.0],
            'value2_A': [300.0, 0.0],
            'value2_B': [0.0, 800.0],
            'Total value1': [30.0, 70.0],
            'Total value2': [300.0, 800.0]
        })

        # Test aggregation with totals included
        result = self.dp.aggregate_daily_to_wc_wide(
            df=df.copy(),
            date_column='date',
            group_columns=['group'],
            sum_columns=['value1', 'value2'],
            wc='sun',
            aggregation='sum',
            include_totals=True
        )

        # Ensure 'OBS' columns are datetime for comparison
        result['OBS'] = pd.to_datetime(result['OBS'])
        expected_output['OBS'] = pd.to_datetime(expected_output['OBS'])

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_output)

        # Test without group columns (no totals, single wide column)
        expected_output_no_group = pd.DataFrame({
            'OBS': ['2023-01-01', '2023-01-08'],
            'value1': [30.0, 70.0],
            'value2': [300.0, 800.0]
        })

        result_no_group = self.dp.aggregate_daily_to_wc_wide(
            df=df.copy(),
            date_column='date',
            group_columns=[],
            sum_columns=['value1', 'value2'],
            wc='sun',
            aggregation='sum',
            include_totals=False
        )

        # Ensure 'OBS' columns are datetime for comparison
        result_no_group['OBS'] = pd.to_datetime(result_no_group['OBS'])
        expected_output_no_group['OBS'] = pd.to_datetime(expected_output_no_group['OBS'])

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result_no_group, expected_output_no_group)

    def test_merge_cols_with_seperator(self):
        # Create a test DataFrame
        test_data = {
            'col1': ['apple', 'banana', 'cherry'],
            'col2': ['red', 'yellow', 'red'],
            'col3': ['fruit', 'fruit', 'fruit']
        }
        df = pd.DataFrame(test_data)

        # Test merging two columns with default separator
        expected_output_default = df.copy()
        expected_output_default['Merged'] = ['apple_red', 'banana_yellow', 'cherry_red']

        result_default = self.dp.merge_cols_with_seperator(df.copy(), col_names=['col1', 'col2'])
        pd.testing.assert_frame_equal(result_default, expected_output_default)

        # Test merging three columns with custom separator
        expected_output_custom = df.copy()
        expected_output_custom['Merged'] = ['apple-red-fruit', 'banana-yellow-fruit', 'cherry-red-fruit']

        result_custom = self.dp.merge_cols_with_seperator(df.copy(), col_names=['col1', 'col2', 'col3'], seperator='-')
        pd.testing.assert_frame_equal(result_custom, expected_output_custom)

        # Test merging with starting and ending prefix
        expected_output_prefix = df.copy()
        expected_output_prefix['Merged'] = ['Start:apple_red:End', 'Start:banana_yellow:End', 'Start:cherry_red:End']

        result_prefix = self.dp.merge_cols_with_seperator(
            df.copy(),
            col_names=['col1', 'col2'],
            seperator='_',
            starting_prefix_str='Start:',
            ending_prefix_str=':End'
        )
        pd.testing.assert_frame_equal(result_prefix, expected_output_prefix)

        # Test error for less than two columns
        with self.assertRaises(ValueError):
            self.dp.merge_cols_with_seperator(df.copy(), col_names=['col1'])

    def test_check_sum_of_df_cols_are_equal(self):
        # Create test DataFrames
        df1 = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })

        df2 = pd.DataFrame({
            'colA': [1, 2, 3],
            'colB': [4, 5, 6]
        })

        df3 = pd.DataFrame({
            'colX': [1, 2, 3],
            'colY': [4, 5, 7]
        })

        # Test case where sums are equal
        result_equal = self.dp.check_sum_of_df_cols_are_equal(df1, df2, cols_1=['col1', 'col2'], cols_2=['colA', 'colB'])
        self.assertEqual(result_equal[0], "They are equal")
        self.assertEqual(result_equal[1], 21)  # Sum of df1's columns
        self.assertEqual(result_equal[2], 21)  # Sum of df2's columns

        # Test case where sums are not equal
        result_not_equal = self.dp.check_sum_of_df_cols_are_equal(df1, df3, cols_1=['col1', 'col2'], cols_2=['colX', 'colY'])
        self.assertTrue(result_not_equal[0].startswith("They are different by "))
        self.assertEqual(result_not_equal[1], 21)  # Sum of df1's columns
        self.assertEqual(result_not_equal[2], 22)  # Sum of df3's columns

        # Test case with mismatched column names
        with self.assertRaises(KeyError):
            self.dp.check_sum_of_df_cols_are_equal(df1, df2, cols_1=['nonexistent_col'], cols_2=['colA', 'colB'])

        # Test case with empty columns
        result_empty_cols = self.dp.check_sum_of_df_cols_are_equal(df1, df2, cols_1=[], cols_2=[])
        self.assertEqual(result_empty_cols[1], 0)  # Sum of empty columns
        self.assertEqual(result_empty_cols[2], 0)  # Sum of empty columns
        self.assertEqual(result_empty_cols[0], "They are equal")

    def test_convert_2_df_cols_to_dict(self):
        # Create a test DataFrame
        df = pd.DataFrame({
            'key_col': ['key1', 'key2', 'key3'],
            'value_col': [10, 20, 30]
        })

        # Expected dictionary
        expected_dict = {
            'key1': 10,
            'key2': 20,
            'key3': 30
        }

        # Test basic functionality
        result = self.dp.convert_2_df_cols_to_dict(df, 'key_col', 'value_col')
        self.assertEqual(result, expected_dict)

        # Test with non-unique keys
        df_non_unique = pd.DataFrame({
            'key_col': ['key1', 'key2', 'key1'],
            'value_col': [10, 20, 30]
        })
        expected_dict_non_unique = {
            'key1': 30,  # Last occurrence of 'key1' should overwrite the earlier one
            'key2': 20
        }
        result_non_unique = self.dp.convert_2_df_cols_to_dict(df_non_unique, 'key_col', 'value_col')
        self.assertEqual(result_non_unique, expected_dict_non_unique)

        # Test with missing key or value column
        with self.assertRaises(ValueError):
            self.dp.convert_2_df_cols_to_dict(df, 'missing_key_col', 'value_col')

        with self.assertRaises(ValueError):
            self.dp.convert_2_df_cols_to_dict(df, 'key_col', 'missing_value_col')

        # Test with empty DataFrame
        df_empty = pd.DataFrame(columns=['key_col', 'value_col'])
        expected_empty_dict = {}
        result_empty = self.dp.convert_2_df_cols_to_dict(df_empty, 'key_col', 'value_col')
        self.assertEqual(result_empty, expected_empty_dict)

    def test_keyword_lookup_replacement(self):
        # Create a test DataFrame
        test_data = {
            'col1': ['A', 'B', 'C', 'D'],
            'col2': ['X', 'Y', 'Z', 'W'],
            'value_col': ['old_value', 'old_value', 'unchanged', 'old_value']
        }
        df = pd.DataFrame(test_data)

        # Lookup dictionary for replacements
        lookup_dict = {
            'A|X': 'new_value_1',
            'B|Y': 'new_value_2',
            'D|W': 'new_value_3'
        }

        # Expected output
        expected_output = df.copy()
        expected_output['Updated Column'] = ['new_value_1', 'new_value_2', 'unchanged', 'new_value_3']

        # Apply the function
        result = self.dp.keyword_lookup_replacement(
            df.copy(),
            col='value_col',
            replacement_rows='old_value',
            cols_to_merge=['col1', 'col2'],
            replacement_lookup_dict=lookup_dict
        )

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_output)

        # Test case where no replacement is needed
        df_no_replacement = pd.DataFrame({
            'col1': ['E', 'F'],
            'col2': ['G', 'H'],
            'value_col': ['unchanged', 'unchanged']
        })
        expected_no_replacement = df_no_replacement.copy()
        expected_no_replacement['Updated Column'] = ['unchanged', 'unchanged']

        result_no_replacement = self.dp.keyword_lookup_replacement(
            df_no_replacement.copy(),
            col='value_col',
            replacement_rows='old_value',
            cols_to_merge=['col1', 'col2'],
            replacement_lookup_dict=lookup_dict
        )

        pd.testing.assert_frame_equal(result_no_replacement, expected_no_replacement)
        
    def test_convert_df_wide_2_long(self):
        # Create a test DataFrame
        test_data = {
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score1': [85, 90, 78],
            'score2': [88, 92, 81]
        }
        df = pd.DataFrame(test_data)

        # Expected output for the transformation
        expected_output = pd.DataFrame({
            'id': [1, 2, 3, 1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie', 'Alice', 'Bob', 'Charlie'],
            'Stacked': ['score1', 'score1', 'score1', 'score2', 'score2', 'score2'],
            'Value': [85, 90, 78, 88, 92, 81]
        })

        # Apply the function
        result = self.dp.convert_df_wide_2_long(
            df.copy(),
            value_cols=['score1', 'score2'],
            variable_col_name='Stacked',
            value_col_name='Value'
        )

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_output)

        # Test case with only one column (should raise ValueError)
        with self.assertRaises(ValueError):
            self.dp.convert_df_wide_2_long(
                df.copy(),
                value_cols=['score1'],
                variable_col_name='Stacked',
                value_col_name='Value'
            )

        # Test case with no value columns (should raise ValueError)
        with self.assertRaises(ValueError):
            self.dp.convert_df_wide_2_long(
                df.copy(),
                value_cols=[],
                variable_col_name='Stacked',
                value_col_name='Value'
            )

    def test_format_numbers_with_commas(self):
        # Create a test DataFrame
        test_data = {
            'col1': [1000, 2500000, 12345.678, None],
            'col2': [2000.5, 350000.75, 0, -12345],
            'col3': ['text', 'another text', 50000, 123.45]
        }
        df = pd.DataFrame(test_data).fillna(value=pd.NA)  # Normalize None to pd.NA

        # Expected output with 2 decimal places
        expected_data = {
            'col1': ['1,000.00', '2,500,000.00', '12,345.68', pd.NA],
            'col2': ['2,000.50', '350,000.75', '0.00', '-12,345.00'],
            'col3': ['text', 'another text', '50,000.00', '123.45']
        }
        expected_output = pd.DataFrame(expected_data)

        # Apply the function
        result = self.dp.format_numbers_with_commas(df, decimal_length_chosen=2)

        # Compare the resulting DataFrame with the expected DataFrame
        pd.testing.assert_frame_equal(result, expected_output, check_dtype=False)

    def test_filter_df_on_multiple_conditions(self):
        # Create a test DataFrame
        test_data = {
            'id': [1, 2, 3, 4, 5],
            'value': [10, 20, 30, 40, 50],
            'category': ['A', 'B', 'A', 'C', 'A'],
            'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
        }
        df = pd.DataFrame(test_data)

        # Test Case 1: Single condition (Equality)
        filters_dict = {'category': "== 'A'"}
        expected_output = df[df['category'] == 'A']
        result = self.dp.filter_df_on_multiple_conditions(df, filters_dict)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 2: Multiple conditions (Equality and Greater Than)
        filters_dict = {'category': "== 'A'", 'value': "> 20"}
        expected_output = df[(df['category'] == 'A') & (df['value'] > 20)]
        result = self.dp.filter_df_on_multiple_conditions(df, filters_dict)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 3: Date comparison
        filters_dict = {'date': ">= '2023-01-03'"}
        expected_output = df[df['date'] >= pd.to_datetime('2023-01-03')]
        result = self.dp.filter_df_on_multiple_conditions(df, filters_dict)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 4: Inequality
        filters_dict = {'value': "!= 30"}
        expected_output = df[df['value'] != 30]
        result = self.dp.filter_df_on_multiple_conditions(df, filters_dict)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 5: Mixed conditions
        filters_dict = {'category': "== 'A'", 'date': "<= '2023-01-03'"}
        expected_output = df[(df['category'] == 'A') & (df['date'] <= pd.to_datetime('2023-01-03'))]
        result = self.dp.filter_df_on_multiple_conditions(df, filters_dict)
        pd.testing.assert_frame_equal(result, expected_output)

    def test_fill_weekly_date_range(self):
        # Test input DataFrame
        test_data = {
            'date': ['2023-01-02', '2023-01-16', '2023-01-30'],  # Weekly data with gaps
            'value': [10.0, 20.0, 30.0]
        }
        df = pd.DataFrame(test_data)
        df['date'] = pd.to_datetime(df['date'])

        # Expected output DataFrame
        expected_data = {
            'date': ['2023-01-02', '2023-01-09', '2023-01-16', '2023-01-23', '2023-01-30'],
            'value': [10.0, 0.0, 20.0, 0.0, 30.0]
        }
        expected_output = pd.DataFrame(expected_data)
        expected_output['date'] = pd.to_datetime(expected_output['date'])

        # Call the function
        dp = dataprocessing()  # Replace with the correct instantiation of your class
        result = dp.fill_weekly_date_range(df, date_column='date', freq='W-MON')

        # Assert the result matches the expected output
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_output.reset_index(drop=True))

    def test_add_prefix_and_suffix(self):
        # Test DataFrame
        test_data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'value1': [10, 20, 30],
            'value2': [40, 50, 60]
        }
        df = pd.DataFrame(test_data)

        # Expected output when no date column is excluded
        expected_data_no_date_col = {
            'prefix_date_suffix': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'prefix_value1_suffix': [10, 20, 30],
            'prefix_value2_suffix': [40, 50, 60]
        }
        expected_output_no_date_col = pd.DataFrame(expected_data_no_date_col)

        # Expected output when date column is excluded
        expected_data_with_date_col = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'prefix_value1_suffix': [10, 20, 30],
            'prefix_value2_suffix': [40, 50, 60]
        }
        expected_output_with_date_col = pd.DataFrame(expected_data_with_date_col)

        # Call the function without excluding a date column
        dp = dataprocessing()  # Replace with the correct instantiation of your class
        result_no_date_col = dp.add_prefix_and_suffix(df.copy(), prefix='prefix_', suffix='_suffix')

        # Assert result matches the expected output
        pd.testing.assert_frame_equal(result_no_date_col, expected_output_no_date_col)

        # Call the function with a date column excluded
        result_with_date_col = dp.add_prefix_and_suffix(df.copy(), prefix='prefix_', suffix='_suffix', date_col='date')

        # Assert result matches the expected output
        pd.testing.assert_frame_equal(result_with_date_col, expected_output_with_date_col)

    def test_create_dummies(self):
        # Test Case 1: Basic functionality without date column
        df = pd.DataFrame({
            'col1': [0, 1, 2],
            'col2': [3, 4, 0],
            'col3': [5, 0, 0]
        })
        dummy_threshold = 1
        expected_output = pd.DataFrame({
            'col1': [0, 0, 1],
            'col2': [1, 1, 0],
            'col3': [1, 0, 0]
        })
        result = self.dp.create_dummies(df.copy(), dummy_threshold=dummy_threshold)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 2: With date column
        df_with_date = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'col1': [0, 1, 2],
            'col2': [3, 4, 0]
        })
        expected_output_with_date = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'col1': [0, 0, 1],
            'col2': [1, 1, 0]
        })
        result_with_date = self.dp.create_dummies(df_with_date.copy(), date_col='date', dummy_threshold=dummy_threshold)
        pd.testing.assert_frame_equal(result_with_date, expected_output_with_date)

        # Test Case 3: Adding total dummy column
        expected_output_with_total = expected_output.copy()
        expected_output_with_total['total'] = [1, 1, 1]
        result_with_total = self.dp.create_dummies(df.copy(), dummy_threshold=dummy_threshold, add_total_dummy_col='Yes')
        pd.testing.assert_frame_equal(result_with_total, expected_output_with_total)

        # Test Case 4: Adding total dummy column with date column
        expected_output_with_date_and_total = expected_output_with_date.copy()
        expected_output_with_date_and_total['total'] = [1, 1, 1]
        result_with_date_and_total = self.dp.create_dummies(
            df_with_date.copy(),
            date_col='date',
            dummy_threshold=dummy_threshold,
            add_total_dummy_col='Yes',
        )
        pd.testing.assert_frame_equal(result_with_date_and_total, expected_output_with_date_and_total)

        # Test Case 5: Threshold of 0 (all positive numbers become 1)
        df_threshold_0 = pd.DataFrame({
            'col1': [-1, 0, 1],
            'col2': [0, 2, -3]
        })
        expected_output_threshold_0 = pd.DataFrame({
            'col1': [0, 0, 1],
            'col2': [0, 1, 0]
        })
        result_threshold_0 = self.dp.create_dummies(df_threshold_0.copy(), dummy_threshold=0)
        pd.testing.assert_frame_equal(result_threshold_0, expected_output_threshold_0)

    def test_replace_substrings(self):
        # Test Case 1: Basic replacement
        df = pd.DataFrame({
            'text': ['hello world', 'python programming', 'hello python']
        })
        replacements = {'hello': 'hi', 'python': 'java'}
        expected_output = pd.DataFrame({
            'text': ['hi world', 'java programming', 'hi java']
        })
        result = self.dp.replace_substrings(df.copy(), 'text', replacements)
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 2: Replacement with to_lower=True
        df_mixed_case = pd.DataFrame({
            'text': ['Hello World', 'PYTHON Programming', 'hello PYTHON']
        })
        expected_output_lower = pd.DataFrame({
            'text': ['hi world', 'java programming', 'hi java']
        })
        result_lower = self.dp.replace_substrings(df_mixed_case.copy(), 'text', replacements, to_lower=True)
        pd.testing.assert_frame_equal(result_lower, expected_output_lower)

        # Test Case 3: Replacement with a new column
        df_new_col = pd.DataFrame({
            'text': ['hello world', 'python programming', 'hello python']
        })
        expected_output_new_col = pd.DataFrame({
            'text': ['hello world', 'python programming', 'hello python'],
            'new_text': ['hi world', 'java programming', 'hi java']
        })
        result_new_col = self.dp.replace_substrings(df_new_col.copy(), 'text', replacements, new_column='new_text')
        pd.testing.assert_frame_equal(result_new_col, expected_output_new_col)

    def test_add_total_column(self):
        # Test Case 1: Basic functionality without excluding any column
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6],
            'col3': [7, 8, 9]
        })
        expected_output = df.copy()
        expected_output['Total'] = [12, 15, 18]
        result = self.dp.add_total_column(df.copy())
        pd.testing.assert_frame_equal(result, expected_output)

        # Test Case 2: Excluding a column from the total
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6],
            'col3': [7, 8, 9]
        })
        expected_output_exclude = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6],
            'col3': [7, 8, 9],
            'Total': [5, 7, 9]  # Sum without 'col3'
        })
        result_exclude = self.dp.add_total_column(df.copy(), exclude_col='col3')
        pd.testing.assert_frame_equal(result_exclude, expected_output_exclude)

        # Test Case 3: Custom total column name
        custom_total_col_name = 'Sum'
        expected_output_custom = df.copy()
        expected_output_custom[custom_total_col_name] = [12, 15, 18]
        result_custom = self.dp.add_total_column(df.copy(), total_col_name=custom_total_col_name)
        pd.testing.assert_frame_equal(result_custom, expected_output_custom)

        # Test Case 4: DataFrame with a single column
        single_col_df = pd.DataFrame({'col1': [1, 2, 3]})
        expected_single_col = single_col_df.copy()
        expected_single_col['Total'] = [1, 2, 3]
        result_single_col = self.dp.add_total_column(single_col_df.copy())
        pd.testing.assert_frame_equal(result_single_col, expected_single_col)

    def test_apply_lookup_table_based_on_substring(self):
        # Test Case 1: Basic categorization
        df = pd.DataFrame({
            'text': ['I love apples', 'Bananas are great', 'Something else', 'Grapes are sour']
        })
        category_dict = {
            'apple': 'Fruit',
            'banana': 'Fruit',
            'cherry': 'Fruit',
            'grape': 'Fruit'
        }
        expected_output = pd.DataFrame({
            'text': ['I love apples', 'Bananas are great', 'Something else', 'Grapes are sour'],
            'Category': ['Fruit', 'Fruit', 'Other', 'Fruit']
        })
        result = self.dp.apply_lookup_table_based_on_substring(df.copy(), 'text', category_dict)
        pd.testing.assert_frame_equal(result, expected_output)

    def test_compare_overlap(self):
        """
        Test the compare_overlap function to ensure it calculates differences
        and their totals correctly across overlapping date ranges.
        """
        # 1. Create sample data for df1 (covers 2021-01-01 to 2021-01-04)
        df1_data = [
            {"date": "2021-01-01", "value": 10, "count": 1},
            {"date": "2021-01-02", "value": 15, "count": 2},
            {"date": "2021-01-03", "value": 20, "count": 3},
            {"date": "2021-01-04", "value": 25, "count": 4},
        ]
        df1 = pd.DataFrame(df1_data)

        # 2. Create sample data for df2 (covers 2021-01-03 to 2021-01-05)
        df2_data = [
            {"date": "2021-01-03", "value": 22, "count": 2},
            {"date": "2021-01-04", "value": 20, "count": 5},
            {"date": "2021-01-05", "value": 30, "count": 6},
        ]
        df2 = pd.DataFrame(df2_data)

        # 3. Call compare_overlap from your dataprocessing class
        diff_df, total_diff_df = self.dp.compare_overlap(df1, df2, 'date')
        expected_diff_df = pd.DataFrame({
            'date': pd.to_datetime(['2021-01-03', '2021-01-04']),
            'diff_value': [-2, 5],
            'diff_count': [1, -1]
        })

        expected_total_diff_df = pd.DataFrame({
            'Column': ['value', 'count'],
            'Total Difference': [3, 0]
        })

        # 5. Use pd.testing.assert_frame_equal to check the outputs
        # Sort and reset index to ensure matching row order
        pd.testing.assert_frame_equal(
            diff_df.sort_values('date').reset_index(drop=True),
            expected_diff_df.sort_values('date').reset_index(drop=True)
        )

        # Sort by 'Column' to ensure matching row order in summary
        pd.testing.assert_frame_equal(
            total_diff_df.sort_values('Column').reset_index(drop=True),
            expected_total_diff_df.sort_values('Column').reset_index(drop=True)
        )

    def test_week_commencing_2_week_commencing_conversion_isoweekday(self):
        """
        Test the isoweekday-based function to confirm each date is mapped back
        to the 'week_commencing' day of that ISO week.
        """
        # 2023-01-01 was a Sunday; we'll go through Saturday (7 days).
        df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=7, freq="D")})
        expected_mon = pd.Series(
            [
                pd.Timestamp("2022-12-26"),  # Sunday -> previous Monday
                pd.Timestamp("2023-01-02"),  # Monday
                pd.Timestamp("2023-01-02"),  # Tuesday
                pd.Timestamp("2023-01-02"),  # Wednesday
                pd.Timestamp("2023-01-02"),  # Thursday
                pd.Timestamp("2023-01-02"),  # Friday
                pd.Timestamp("2023-01-02"),  # Saturday
            ],
            name="week_start_mon"
        )

        # Use the new function from our data processing object
        result = self.dp.week_commencing_2_week_commencing_conversion_isoweekday(
            df.copy(),
            date_col="date",
            week_commencing="mon"
        )

        # Compare the 'week_start_mon' column with our expected results
        pd.testing.assert_series_equal(
            result["week_start_mon"],  # actual
            expected_mon               # expected
        )



###################################################################################################################################################
###################################################################################################################################################

# class TestDataPull(unittest.TestCase)


if __name__ == '__main__':
    unittest.main()
