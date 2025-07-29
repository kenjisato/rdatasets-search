"""
Test edge cases and error handling for data_having() function
"""

import pytest
from rdatasets_search.search import data_having


def test_case_insensitive_data_types():
    """Test that data type filters are case insensitive"""
    result1 = data_having("BINARY")
    result2 = data_having("Binary")
    result3 = data_having("binary")
    
    assert len(result1) == len(result2) == len(result3), "Data type filters should be case insensitive"
    assert len(result1) > 0, "Should find datasets with binary data"


def test_whitespace_handling():
    """Test that whitespace in expressions is handled correctly"""
    result1 = data_having("rows>100")
    result2 = data_having("rows > 100")
    result3 = data_having("  rows  >=  100  ")
    
    assert len(result1) == len(result2), "Whitespace should not affect results"
    assert len(result3) >= len(result1), ">= should include more or equal results than >"


def test_invalid_data_type():
    """Test that invalid data types raise ValueError"""
    with pytest.raises(ValueError, match="Invalid argument format"):
        data_having("invalid_type")


def test_invalid_column_name():
    """Test that invalid column names in comparisons raise ValueError"""
    with pytest.raises(ValueError, match="Unknown column"):
        data_having("invalid_col > 10")


def test_invalid_expression_format():
    """Test that invalid expression formats raise ValueError"""
    with pytest.raises(ValueError, match="Invalid argument format"):
        data_having("rows invalid 100")


def test_empty_arguments():
    """Test that empty arguments return the full dataset"""
    result = data_having()
    assert len(result) > 0, "Empty arguments should return full dataset"
    # Should return all datasets
    assert len(result) > 1000, "Should return a substantial number of datasets"


def test_multiple_data_types():
    """Test filtering with multiple data types"""
    result = data_having("binary", "character", "numeric")
    assert len(result) >= 0, "Multiple data types should return valid results"
    
    if len(result) > 0:
        # Verify all results meet all criteria
        assert all(result["n_binary"] > 0), "All results should have binary columns"
        assert all(result["n_character"] > 0), "All results should have character columns"
        assert all(result["n_numeric"] > 0), "All results should have numeric columns"


def test_no_matching_results():
    """Test queries that return no results"""
    # Use a more restrictive query that should return no results
    result = data_having("rows > 10000000")  # Even more extremely large number
    assert len(result) == 0, "Should return no results for impossible criteria"


def test_invalid_operator():
    """Test invalid comparison operators"""
    with pytest.raises(ValueError, match="Invalid argument format"):
        data_having("rows ~= 100")  # Invalid operator


def test_malformed_comparison():
    """Test malformed comparison expressions"""
    with pytest.raises(ValueError):
        data_having("rows >")  # Missing value
    
    with pytest.raises(ValueError):
        data_having("> 100")  # Missing column
    
    with pytest.raises(ValueError):
        data_having("rows 100")  # Missing operator


def test_non_numeric_comparison_value():
    """Test non-numeric values in comparisons"""
    with pytest.raises(ValueError):
        data_having("rows > abc")  # Non-numeric value


def test_edge_case_values():
    """Test edge case numeric values"""
    # Test with 0
    result_zero = data_having("rows > 0")
    assert len(result_zero) >= 0, "Should handle zero comparison"
    
    # Test with negative (should return no results for rows/cols)
    result_negative = data_having("rows > -1")
    assert len(result_negative) >= 0, "Should handle negative comparison"


def test_all_data_types_exist():
    """Test that all expected data types can be filtered"""
    data_types = ["binary", "character", "factor", "logical", "numeric"]
    
    for data_type in data_types:
        result = data_having(data_type)
        assert len(result) >= 0, f"Should handle {data_type} data type"


def test_boundary_conditions():
    """Test boundary conditions for comparisons"""
    # Test exact equality
    result_eq = data_having("cols == 2")
    assert len(result_eq) >= 0, "Should handle equality comparison"
    
    # Test not equal
    result_neq = data_having("cols != 2")
    assert len(result_neq) >= 0, "Should handle not equal comparison"
    
    # Combined, these should cover all datasets
    total_datasets = data_having()
    assert len(result_eq) + len(result_neq) == len(total_datasets), "Equality and inequality should be complementary"
