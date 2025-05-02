import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

class datavis: 
    
    def help(self):
        """
        Displays a help menu listing all the available functions with their descriptions, usage, and examples.
        """        
        print("1. plot_one")
        print("   - Description: Plots a specified column from a DataFrame with white background and black axes.")
        print("   - Usage: plot_one(df1, col1, date_column)")
        print("   - Example: plot_one(df, 'sales', 'date')\n")
        
        print("2. plot_two")
        print("   - Description: Plots specified columns from two DataFrames, optionally on the same or separate y-axes.")
        print("   - Usage: plot_two(df1, col1, df2, col2, date_column, same_axis=True)")
        print("   - Example: plot_two(df1, 'sales_vol', df2, 'sales_revenue', 'date', same_axis=False)\n")
        
        print("3. plot_chart")
        print("   - Description: Plots various chart types using Plotly, including line, bar, scatter, area, pie, etc.")
        print("   - Usage: plot_chart(df, date_col, value_cols, chart_type='line', title='Chart', x_title='Date', y_title='Values')")
        print("   - Example: plot_chart(df, 'date', ['sales', 'revenue'], chart_type='line', title='Sales and Revenue')\n")
    
    def plot_one(self, df1, col1, date_column):
        """
        Plots specified column from a DataFrame with white background and black axes,
        using a specified date column as the X-axis.

        :param df1: DataFrame
        :param col1: Column name from the DataFrame
        :param date_column: The name of the date column to use for the X-axis
        """
        # Check if columns exist in the DataFrame
        if col1 not in df1.columns or date_column not in df1.columns:
            raise ValueError("Column not found in DataFrame")

        # Check if the date column is in datetime format, if not convert it
        if not pd.api.types.is_datetime64_any_dtype(df1[date_column]):
            try:
                # Convert with dayfirst=True to interpret dates correctly
                df1[date_column] = pd.to_datetime(df1[date_column], dayfirst=True)
            except Exception as e:
                raise ValueError(f"Error converting {date_column} to datetime: {e}")

        # Plotting using Plotly Express
        fig = px.line(df1, x=date_column, y=col1)

        # Update layout for white background and black axes lines, and setting y-axis to start at 0
        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(
                showline=True,
                linecolor='black'
            ),
            yaxis=dict(
                showline=True,
                linecolor='black',
                rangemode='tozero'  # Setting Y-axis to start at 0 if suitable
            )
        )

        return fig

    def plot_two(self, df1, col1, df2, col2, date_column, same_axis=True):
        """
        Plots specified columns from two different DataFrames with both different and the same lengths,
        using a specified date column as the X-axis, and charting on either the same or separate y-axes.

        :param df1: First DataFrame
        :param col1: Column name from the first DataFrame
        :param df2: Second DataFrame
        :param col2: Column name from the second DataFrame
        :param date_column: The name of the date column to use for the X-axis
        :param same_axis: If True, plot both traces on the same y-axis; otherwise, use separate y-axes.
        :return: Plotly figure
        """
        # Validate inputs
        if col1 not in df1.columns or date_column not in df1.columns:
            raise ValueError(f"Column {col1} or {date_column} not found in the first DataFrame.")
        if col2 not in df2.columns or date_column not in df2.columns:
            raise ValueError(f"Column {col2} or {date_column} not found in the second DataFrame.")

        # Ensure date columns are in datetime format
        df1[date_column] = pd.to_datetime(df1[date_column], errors='coerce')
        df2[date_column] = pd.to_datetime(df2[date_column], errors='coerce')

        # Drop rows with invalid dates
        df1 = df1.dropna(subset=[date_column])
        df2 = df2.dropna(subset=[date_column])

        # Create traces for the first and second DataFrames
        trace1 = go.Scatter(x=df1[date_column], y=df1[col1], mode='lines', name=col1, yaxis='y1')

        if same_axis:
            trace2 = go.Scatter(x=df2[date_column], y=df2[col2], mode='lines', name=col2, yaxis='y1')
        else:
            trace2 = go.Scatter(x=df2[date_column], y=df2[col2], mode='lines', name=col2, yaxis='y2')

        # Define layout for the plot
        layout = go.Layout(
            title="Comparison Plot",
            xaxis=dict(title=date_column, showline=True, linecolor='black'),
            yaxis=dict(
                title=col1 if same_axis else f"{col1} (y1)",
                showline=True,
                linecolor='black',
                rangemode='tozero'
            ),
            yaxis2=dict(
                title=f"{col2} (y2)" if not same_axis else "",
                overlaying='y',
                side='right',
                showline=True,
                linecolor='black',
                rangemode='tozero'
            ),
            showlegend=True,
            plot_bgcolor='white'  # Set the plot background color to white
        )

        # Create the figure with the defined layout and traces
        fig = go.Figure(data=[trace1, trace2], layout=layout)

        return fig

    def plot_chart(self, df, date_col, value_cols, chart_type='line', title='Chart', x_title='Date', y_title='Values', **kwargs):
        """
        Plot various types of charts using Plotly.

        Args:
            df (pandas.DataFrame): DataFrame containing the data.
            date_col (str): The name of the column with date information.
            value_cols (list): List of columns to plot.
            chart_type (str): Type of chart to plot ('line', 'bar', 'scatter', etc.).
            title (str): Title of the chart.
            x_title (str): Title of the x-axis.
            y_title (str): Title of the y-axis.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            plotly.graph_objects.Figure: The Plotly figure object.
        """
        import pandas as pd
        import plotly.graph_objects as go

        # Ensure the date column is in datetime format
        df[date_col] = pd.to_datetime(df[date_col])

        # Validate input columns
        value_cols = [col for col in value_cols if col in df.columns and col != date_col]
        if not value_cols:
            raise ValueError("No valid columns provided for plotting.")

        # Initialize the figure
        fig = go.Figure()

        # Define a mapping for chart types to corresponding Plotly trace types
        chart_trace_map = {
            'line': lambda col: go.Scatter(x=df[date_col], y=df[col], mode='lines', name=col, **kwargs),
            'bar': lambda col: go.Bar(x=df[date_col], y=df[col], name=col, **kwargs),
            'scatter': lambda col: go.Scatter(x=df[date_col], y=df[col], mode='markers', name=col, **kwargs),
            'area': lambda col: go.Scatter(x=df[date_col], y=df[col], mode='lines', fill='tozeroy', name=col, **kwargs),
            'pie': lambda col: go.Pie(labels=df[date_col], values=df[col], name=col, **kwargs),
            'box': lambda col: go.Box(y=df[col], name=col, **kwargs),
            'bubble': lambda _: go.Scatter(
                x=df[value_cols[0]], y=df[value_cols[1]], mode='markers',
                marker=dict(size=df[value_cols[2]]), name='Bubble Chart', **kwargs
            ),
            'funnel': lambda col: go.Funnel(y=df[date_col], x=df[col], **kwargs),
            'waterfall': lambda col: go.Waterfall(x=df[date_col], y=df[col], measure=df[value_cols[1]], **kwargs),
            'scatter3d': lambda _: go.Scatter3d(
                x=df[value_cols[0]], y=df[value_cols[1]], z=df[value_cols[2]],
                mode='markers', **kwargs
            )
        }

        # Generate traces for the selected chart type
        if chart_type in chart_trace_map:
            for col in value_cols:
                trace = chart_trace_map[chart_type](col)
                fig.add_trace(trace)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Update the layout of the figure
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            legend_title='Series',
            template='plotly_dark'
        )

        return fig