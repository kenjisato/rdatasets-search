"""
Test script for the data_having() function
"""

import pytest
from rdatasets_search.search import data_having


def test_binary_data_filter():
    """Test filtering for datasets with binary data"""
    binary_data = data_having("binary")
    assert len(binary_data) > 0, "Should find datasets with binary data"
    # Verify all results have binary columns
    assert all(binary_data["n_binary"] > 0), "All results should have binary columns"


def test_character_data_filter():
    """Test filtering for datasets with character data"""
    character_data = data_having("character")
    assert len(character_data) > 0, "Should find datasets with character data"
    # Verify all results have character columns
    assert all(character_data["n_character"] > 0), "All results should have character columns"


def test_rows_greater_than_filter():
    """Test filtering for datasets with more than 100 rows"""
    large_datasets = data_having("rows > 100")
    assert len(large_datasets) > 0, "Should find datasets with > 100 rows"
    # Verify all results have more than 100 rows
    assert all(large_datasets["Rows"] > 100), "All results should have > 100 rows"


def test_exact_columns_filter():
    """Test filtering for datasets with exactly 5 columns"""
    five_col_datasets = data_having("cols == 5")
    assert len(five_col_datasets) > 0, "Should find datasets with exactly 5 columns"
    # Verify all results have exactly 5 columns
    assert all(five_col_datasets["Cols"] == 5), "All results should have exactly 5 columns"


def test_combined_filters():
    """Test combining multiple filters"""
    combined = data_having("binary", "numeric", "rows > 50")
    assert len(combined) >= 0, "Combined filter should return valid results"
    if len(combined) > 0:
        # Verify all results meet all criteria
        assert all(combined["n_binary"] > 0), "All results should have binary columns"
        assert all(combined["n_numeric"] > 0), "All results should have numeric columns"
        assert all(combined["Rows"] > 50), "All results should have > 50 rows"


def test_various_operators():
    """Test different comparison operators"""
    # Less than
    small_datasets = data_having("rows < 50")
    assert len(small_datasets) >= 0, "Should handle < operator"
    if len(small_datasets) > 0:
        assert all(small_datasets["Rows"] < 50), "All results should have < 50 rows"
    
    # Greater than or equal
    medium_datasets = data_having("rows >= 100")
    assert len(medium_datasets) >= 0, "Should handle >= operator"
    if len(medium_datasets) > 0:
        assert all(medium_datasets["Rows"] >= 100), "All results should have >= 100 rows"
    
    # Not equal
    not_five_cols = data_having("cols != 5")
    assert len(not_five_cols) >= 0, "Should handle != operator"
    if len(not_five_cols) > 0:
        assert all(not_five_cols["Cols"] != 5), "All results should not have 5 columns"


def test_less_than_equal_operator():
    """Test <= operator"""
    small_datasets = data_having("rows <= 50")
    assert len(small_datasets) >= 0, "Should handle <= operator"
    if len(small_datasets) > 0:
        assert all(small_datasets["Rows"] <= 50), "All results should have <= 50 rows"


def test_multiple_data_types():
    """Test filtering for multiple data types"""
    result = data_having("binary", "character")
    assert len(result) >= 0, "Should handle multiple data types"
    if len(result) > 0:
        assert all(result["n_binary"] > 0), "All results should have binary columns"
        assert all(result["n_character"] > 0), "All results should have character columns"


def test_numeric_data_filter():
    """Test filtering for datasets with numeric data"""
    numeric_data = data_having("numeric")
    assert len(numeric_data) > 0, "Should find datasets with numeric data"
    assert all(numeric_data["n_numeric"] > 0), "All results should have numeric columns"


def test_factor_data_filter():
    """Test filtering for datasets with factor data"""
    factor_data = data_having("factor")
    assert len(factor_data) >= 0, "Should handle factor data filter"
    if len(factor_data) > 0:
        assert all(factor_data["n_factor"] > 0), "All results should have factor columns"


def test_logical_data_filter():
    """Test filtering for datasets with logical data"""
    logical_data = data_having("logical")
    assert len(logical_data) >= 0, "Should handle logical data filter"
    if len(logical_data) > 0:
        assert all(logical_data["n_logical"] > 0), "All results should have logical columns"
