import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta.types import OrderBy
from google.analytics.data_v1beta.types import Filter
from google.analytics.data_v1beta.types import FilterExpression
from google.analytics.data_v1beta.types import FilterExpressionList
from google.auth.exceptions import DefaultCredentialsError
import logging
from datetime import datetime, timedelta
import os
import numpy as np
from scipy.spatial import cKDTree

class geoprocessing:
    
    def help(self):
        
        print("\n1. pull_ga")
        print("   - Description: Pull in GA4 data for geo experiments.")
        print("   - Usage: pull_ga(credentials_file, property_id, start_date, country, metrics)")
        print("   - Example: pull_ga('GeoExperiment-31c5f5db2c39.json', '111111111', '2023-10-15', 'United Kingdom', ['totalUsers', 'newUsers'])")

        print("\n2. process_itv_analysis")
        print("   - Description: Processes region-level data for geo experiments by mapping ITV regions, grouping selected metrics, merging with media spend data, and saving the result.")
        print("   - Usage: process_itv_analysis(raw_df, itv_path, cities_path, media_spend_path, output_path, test_group, control_group, columns_to_aggregate, aggregator_list")
        print("   - Example: process_itv_analysis(df, 'itv_regional_mapping.csv', 'Geo_Mappings_with_Coordinates.xlsx', 'IMS.xlsx', 'itv_for_test_analysis_itvx.csv', ['West', 'Westcountry', 'Tyne Tees'], ['Central Scotland', 'North Scotland'], ['newUsers', 'transactions'], ['sum', 'sum']")
        
        print("\n3. process_city_analysis")
        print("   - Description: Processes city-level data for geo experiments by grouping selected metrics, merging with media spend data, and saving the result.")
        print("   - Usage: process_city_analysis(raw_data, spend_data, output_path, test_group, control_group, columns_to_aggregate, aggregator_list)")
        print("   - Example: process_city_analysis(df, spend, 'output.csv', ['Barnsley'], ['Aberdeen'], ['newUsers', 'transactions'], ['sum', 'mean'])")
                
    def pull_ga(self, credentials_file, property_id, start_date, country, metrics):
        """
        Pulls Google Analytics data using the BetaAnalyticsDataClient.

        Parameters:
        credentials_file (str): Path to the JSON credentials file.
        property_id (str): Google Analytics property ID.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        country (str): Country to filter the data by.
        metrics (list): List of metrics to retrieve (e.g., ["totalUsers", "sessions"]).

        Returns:
        pd.DataFrame: A pandas DataFrame containing the fetched data.
        """
        try:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file '{credentials_file}' not found.")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file

            try:
                client = BetaAnalyticsDataClient()
            except DefaultCredentialsError as e:
                raise DefaultCredentialsError(
                    f"Failed to initialize Google Analytics client: {e}"
                )

            def format_report(request):
                response = client.run_report(request)
                # Row index
                row_index_names = [header.name for header in response.dimension_headers]
                row_header = []
                for i in range(len(row_index_names)):
                    row_header.append([row.dimension_values[i].value for row in response.rows])

                row_index_named = pd.MultiIndex.from_arrays(np.array(row_header), names=np.array(row_index_names))
                # Row flat data
                metric_names = [header.name for header in response.metric_headers]
                data_values = []
                for i in range(len(metric_names)):
                    data_values.append([row.metric_values[i].value for row in response.rows])

                output = pd.DataFrame(data=np.transpose(np.array(data_values, dtype='f')),
                                    index=row_index_named, columns=metric_names)
                return output

            all_dfs = []
            offset_value = 0
            batch_size = 100000  

            while True:
                metric_objects = [Metric(name=metric) for metric in metrics]

                request = RunReportRequest(
                    property='properties/' + property_id,
                    dimensions=[Dimension(name="date"), Dimension(name="city")],
                    metrics=metric_objects,
                    order_bys=[OrderBy(dimension={'dimension_name': 'date'}),
                            OrderBy(dimension={'dimension_name': 'city'})],
                    date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                    limit=batch_size,
                    offset=offset_value,
                    dimension_filter=FilterExpression(
                        and_group=FilterExpressionList(
                            expressions=[
                                FilterExpression(
                                    filter=Filter(
                                        field_name="country",
                                        string_filter=Filter.StringFilter(value=country),
                                    )
                                ),
                            ]
                        )
                    )
                )

                df = format_report(request)
                if df.empty:
                    break 

                df = df.reset_index()
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                all_dfs.append(df)
                offset_value += batch_size

            if not all_dfs:
                return pd.DataFrame() 

            final_df = pd.concat(all_dfs, ignore_index=True)
            return final_df

        except FileNotFoundError as e:
            logging.error(f"FileNotFoundError: {e}")
            raise
        except DefaultCredentialsError as e:
            logging.error(f"DefaultCredentialsError: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    def process_itv_analysis(self, raw_df, city_lut, itv_lut, test_list, control_list):
        """
        Process the raw data by merging it with a city lookup table,
        performing a spatial join to find the nearest ITV region,
        automatically aggregating metric columns (all columns from raw_df except 'date' and 'geo'),
        and assigning a numerical group based on provided test and control lists.

        Parameters:
            raw_df (pd.DataFrame): Raw data containing at least the columns 'date' and 'geo'
                                plus metric columns that should be summed.
            city_lut (pd.DataFrame): City lookup table DataFrame with a column 'geo' and coordinate data.
            itv_lut (pd.DataFrame): ITV lookup table DataFrame with columns 'Latitude', 'Longitude', and 'ITV Region'
                                    for spatial matching.
            test_list (list): List of region names (strings) to be assigned the value 1.
            control_list (list): List of region names (strings) to be assigned the value 2.

        Returns:
            pd.DataFrame: Aggregated DataFrame grouped by 'date' and 'geo' (where 'geo' comes from ITV Region),
                        with the metric columns summed and an additional 'assignment' column.
        """
        
        # Ensure the ITV lookup table has valid coordinate data
        itv_lut = itv_lut.dropna(subset=['Latitude', 'Longitude'])
        
        # Merge raw_df with the city lookup table on 'geo'
        merged_df = pd.merge(raw_df, city_lut, on='geo', how='left')
        
        # Build a KD-tree from the ITV lookup table's coordinates for an efficient nearest-neighbor search
        tree = cKDTree(itv_lut[['Latitude', 'Longitude']].values)
        
        # For each record in merged_df, find the nearest ITV region based on coordinates
        distances, indices = tree.query(merged_df[['Latitude', 'Longitude']].values, k=1)
        
        # Map the nearest ITV Region back to merged_df
        merged_df['ITV Region'] = itv_lut.iloc[indices]['ITV Region'].values
        
        # Automatically determine the metric columns from raw_df (all columns except 'date' and 'geo')
        metric_cols = [col for col in raw_df.columns if col not in ['date', 'geo']]
        
        # Aggregate (sum) the metric columns, grouping by 'date' and the nearest ITV Region
        aggregated_df = merged_df.groupby(['date', 'ITV Region'], as_index=False)[metric_cols].sum()
        
        # Rename 'ITV Region' to 'geo' to be consistent with your downstream usage
        aggregated_df.rename(columns={'ITV Region': 'geo'}, inplace=True)
        
        # Define a function to assign group values based on the region name
        def assign_value(region):
            if region in test_list:
                return 1
            elif region in control_list:
                return 2
            else:
                return np.nan  # Or another default value if desired
        
        # Apply the assignment function and remove rows without a valid assignment
        aggregated_df['assignment'] = aggregated_df['geo'].apply(assign_value)
        aggregated_df.dropna(subset=['assignment'], inplace=True)
        aggregated_df['assignment'] = aggregated_df['assignment'].astype(int)
        
        return aggregated_df
    
    def process_city_analysis(self, raw_data, spend_data, output_path, test_group, control_group, columns_to_aggregate, aggregator_list):
        """
        Process city-level analysis by grouping data, applying custom aggregations, 
        and merging with spend data.

        Parameters:
            raw_data (str or pd.DataFrame):
                - Raw input data as a file path (CSV/XLSX) or a DataFrame.
                - Must contain 'date' and 'city' columns, plus any columns to be aggregated.
            spend_data (str or pd.DataFrame):
                - Spend data as a file path (CSV/XLSX) or a DataFrame.
                - Must contain 'date', 'geo', and 'cost' columns.
            output_path (str): 
                - Path to save the final output file (CSV or XLSX).
            group1 (list): 
                - List of city regions to be considered "Test Group" or "Group 1".
            group2 (list): 
                - List of city regions to be considered "Control Group" or "Group 2".
            columns_to_aggregate (list): 
                - List of columns to apply aggregation to, e.g. ['newUsers', 'transactions'].
            aggregator_list (list): 
                - List of corresponding aggregation functions, e.g. ['sum', 'mean'].
                - Must be the same length as columns_to_aggregate.

        Returns:
            pd.DataFrame: The final merged, aggregated DataFrame.
        """

        def read_file(data):
            """Helper function to handle file paths or return DataFrame directly."""
            if isinstance(data, pd.DataFrame):
                return data
            ext = os.path.splitext(data)[1].lower()
            if ext == '.csv':
                return pd.read_csv(data)
            elif ext in ['.xlsx', '.xls']:
                return pd.read_excel(data)
            else:
                raise ValueError("Unsupported file type. Please use a CSV or XLSX file.")

        def write_file(df, file_path):
            """Helper function to write DataFrame to CSV or XLSX files."""
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                df.to_csv(file_path, index=False)
            elif ext in ['.xlsx', '.xls']:
                df.to_excel(file_path, index=False, engine='openpyxl')
            else:
                raise ValueError("Unsupported file type. Please use a CSV or XLSX file.")

        # -----------------------
        # 1. Read and validate data
        # -----------------------
        raw_df = read_file(raw_data)
        raw_df = raw_df.rename(columns={'city': 'geo'})
        spend_df = read_file(spend_data).rename(columns={'Cost': 'cost'})

        # Columns we minimally need in raw_df
        required_columns = {'date', 'geo'}
        # Ensure the columns to aggregate are there
        required_columns = required_columns.union(set(columns_to_aggregate))
        missing_in_raw = required_columns - set(raw_df.columns)
        if missing_in_raw:
            raise ValueError(
                f"The raw data is missing the following required columns: {missing_in_raw}"
            )

        # Validate spend data
        spend_required_columns = {'date', 'geo', 'cost'}
        missing_in_spend = spend_required_columns - set(spend_df.columns)
        if missing_in_spend:
            raise ValueError(
                f"The spend data is missing the following required columns: {missing_in_spend}"
            )

        # -----------------------
        # 2. Clean and prepare spend data
        # -----------------------
        # Convert cost column to numeric after stripping currency symbols and commas
        spend_df['cost'] = (
            spend_df['cost']
            .replace('[^\\d.]', '', regex=True)
            .astype(float)
        )

        # -----------------------
        # 3. Prepare raw data
        # -----------------------
        # Filter only the relevant geos
        filtered_df = raw_df[raw_df['geo'].isin(test_group + control_group)].copy()
        # -----------------------
        # 4. Group and aggregate
        # -----------------------
        # Create a dictionary of {col: agg_function}
        if len(columns_to_aggregate) != len(aggregator_list):
            raise ValueError(
                "columns_to_aggregate and aggregator_list must have the same length."
            )
        aggregation_dict = dict(zip(columns_to_aggregate, aggregator_list))

        # Perform groupby using the aggregator dictionary
        grouped_df = filtered_df.groupby(['date', 'geo'], as_index=False).agg(aggregation_dict)

        # -----------------------
        # 5. Map groups (Test vs. Control)
        # -----------------------        
        assignment_map = {city: 1 for city in test_group}
        assignment_map.update({city: 2 for city in control_group})
        grouped_df['assignment'] = grouped_df['geo'].map(assignment_map)

        # -----------------------
        # 6. Merge with spend data
        # -----------------------
        merged_df = pd.merge(
            grouped_df,
            spend_df,  # has date, geo, cost
            on=['date', 'geo'],
            how='left'
        )

        # Fill missing cost with 0
        merged_df['cost'] = merged_df['cost'].fillna(0)

        # -----------------------
        # 7. Write out results
        # -----------------------
        write_file(merged_df, output_path)

        return merged_df