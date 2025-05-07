# import pandas as pd

# class Transform:
#     @staticmethod
#     def clean_data(data: pd.DataFrame) -> pd.DataFrame:
#         """Drop rows with missing values."""
#         return data.dropna()

#     @staticmethod
#     def aggregate_data(data: pd.DataFrame, group_by: str, agg_func='sum') -> pd.DataFrame:
#         """Aggregate data based on a column and aggregation function."""
#         return data.groupby(group_by).agg(agg_func)

#     @staticmethod
#     def format_data(data: pd.DataFrame) -> pd.DataFrame:
#         """Convert all column names to lowercase."""
#         data.columns = [col.lower() for col in data.columns]
#         return data
import pandas as pd
from typing import Dict, List, Union, Callable

class Transform:
    def __init__(self):
        self.transformations = []

    def add_clean_data(self, columns: List[str] = None, strategy: str = 'drop') -> 'Transform':
        """
        Add a cleaning step.
        - columns: List of columns to clean (if None, applies to all).
        - strategy: 'drop' to drop rows with NaN, 'fill' to fill with a value.
        """
        def clean(data: pd.DataFrame) -> pd.DataFrame:
            df = data.copy()
            if columns:
                df = df.dropna(subset=columns) if strategy == 'drop' else df.fillna(0, subset=columns)
            else:
                df = df.dropna() if strategy == 'drop' else df.fillna(0)
            return df
        self.transformations.append(clean)
        return self

    def add_aggregate_data(self, group_by: Union[str, List[str]], aggregations: Dict[str, Callable]) -> 'Transform':
        """
        Add an aggregation step.
        - group_by: Column(s) to group by.
        - aggregations: Dict of column names to aggregation functions (e.g., {'temperature': 'mean'}).
        """
        def aggregate(data: pd.DataFrame) -> pd.DataFrame:
            return data.groupby(group_by).agg(aggregations).reset_index()
        self.transformations.append(aggregate)
        return self

    def add_format_data(self, lowercase_columns: bool = True) -> 'Transform':
        """Add a formatting step (e.g., lowercase column names)."""
        def format_data(data: pd.DataFrame) -> pd.DataFrame:
            df = data.copy()
            if lowercase_columns:
                df.columns = [col.lower() for col in df.columns]
            return df
        self.transformations.append(format_data)
        return self

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply all transformations in sequence."""
        df = data.copy()
        for transform in self.transformations:
            df = transform(df)
        return df

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'City': ['Nairobi', 'Nairobi', 'Mombasa'],
        'Temperature': [25, 26, 28],
        'Humidity': [60, None, 65]
    })
    transformer = Transform()
    transformer.add_clean_data(strategy='fill')
    transformer.add_aggregate_data(group_by='City', aggregations={'Temperature': 'mean', 'Humidity': 'mean'})
    transformer.add_format_data()
    result = transformer.apply(data)
    print(result)