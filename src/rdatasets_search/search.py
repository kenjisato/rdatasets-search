import polars as pl
import re

csv_index = "https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/datasets.csv"
rdatasets = pl.read_csv(csv_index)

def data_having(*args):
    """
    Allowed arguments:
      - binary, character, factor, logical, numeric
      - rows > 100, cols == 5, etc.

    Filters with the given query arguments and returns the subset.
    """
    
    # Start with the full dataset
    filtered_data = rdatasets
    
    # Define mapping for data type arguments to column names
    data_type_columns = {
        'binary': 'n_binary',
        'character': 'n_character', 
        'factor': 'n_factor',
        'logical': 'n_logical',
        'numeric': 'n_numeric'
    }
    
    # Define mapping for comparison column names
    comparison_columns = {
        'rows': 'Rows',
        'cols': 'Cols'
    }
    
    for arg in args:
        arg = arg.strip()
        
        # Check if it's a data type filter
        if arg.lower() in data_type_columns:
            col_name = data_type_columns[arg.lower()]
            filtered_data = filtered_data.filter(pl.col(col_name) > 0)
            
        else:
            # Parse comparison expression
            # Pattern: column_name operator value
            # Supports: >, <, >=, <=, ==, !=
            pattern = r'(\w+)\s*(>=|<=|==|!=|>|<)\s*(-?\d+)'
            match = re.match(pattern, arg)
            
            if match:
                col_name_key, operator, value_str = match.groups()
                
                # Map to actual column name (case insensitive)
                if col_name_key.lower() in comparison_columns:
                    actual_col_name = comparison_columns[col_name_key.lower()]
                    value = int(value_str)
                    
                    # Apply the filter based on operator
                    if operator == '>':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) > value)
                    elif operator == '<':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) < value)
                    elif operator == '>=':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) >= value)
                    elif operator == '<=':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) <= value)
                    elif operator == '==':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) == value)
                    elif operator == '!=':
                        filtered_data = filtered_data.filter(pl.col(actual_col_name) != value)
                else:
                    raise ValueError(f"Unknown column name: {col_name_key}. Supported: rows, cols")
            else:
                raise ValueError(f"Invalid argument format: {arg}. Expected format: 'column operator value' (e.g., 'rows > 100') or data type name (e.g., 'binary')")
    
    return filtered_data
