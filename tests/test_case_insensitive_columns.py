"""
Test case insensitive column names in comparison expressions
"""

import pytest
from rdatasets_search.search import data_having


def test_rows_column_case_insensitive():
    """Test that 'rows' column comparisons are case insensitive"""
    test_cases = [
        "rows > 100",
        "ROWS > 100", 
        "Rows > 100",
        "rOwS > 100"
    ]
    
    results = []
    for case in test_cases:
        result = data_having(case)
        results.append(len(result))
    
    # All case variations should return the same number of results
    assert all(r == results[0] for r in results), "All case variations should return the same results"
    assert results[0] > 0, "Should find datasets with > 100 rows"


def test_cols_column_case_insensitive():
    """Test that 'cols' column comparisons are case insensitive"""
    test_cases = [
        "cols == 5",
        "COLS == 5",
        "Cols == 5", 
        "cOlS == 5"
    ]
    
    results = []
    for case in test_cases:
        result = data_having(case)
        results.append(len(result))
    
    # All case variations should return the same number of results
    assert all(r == results[0] for r in results), "All case variations should return the same results"


def test_mixed_case_combinations():
    """Test mixed case combinations of data types and column comparisons"""
    test_cases = [
        ("BINARY", "ROWS > 50"),
        ("binary", "rows > 50"),
        ("Binary", "Rows > 50"),
        ("BINARY", "rows > 50"),
        ("binary", "ROWS > 50")
    ]
    
    results = []
    for data_type, size_filter in test_cases:
        result = data_having(data_type, size_filter)
        results.append(len(result))
    
    # All mixed case combinations should return the same results
    assert all(r == results[0] for r in results), "All mixed case combinations should return the same results"


def test_data_type_case_insensitive():
    """Test that data type filters are case insensitive"""
    # Test binary
    binary_lower = data_having("binary")
    binary_upper = data_having("BINARY")
    binary_mixed = data_having("Binary")
    
    assert len(binary_lower) == len(binary_upper) == len(binary_mixed), "Binary filter should be case insensitive"
    
    # Test character
    char_lower = data_having("character")
    char_upper = data_having("CHARACTER")
    char_mixed = data_having("Character")
    
    assert len(char_lower) == len(char_upper) == len(char_mixed), "Character filter should be case insensitive"
    
    # Test numeric
    num_lower = data_having("numeric")
    num_upper = data_having("NUMERIC")
    num_mixed = data_having("Numeric")
    
    assert len(num_lower) == len(num_upper) == len(num_mixed), "Numeric filter should be case insensitive"


def test_complex_case_insensitive_query():
    """Test complex queries with mixed case"""
    result1 = data_having("BINARY", "CHARACTER", "rows > 100", "cols <= 10")
    result2 = data_having("binary", "character", "ROWS > 100", "COLS <= 10")
    result3 = data_having("Binary", "Character", "Rows > 100", "Cols <= 10")
    
    assert len(result1) == len(result2) == len(result3), "Complex queries should be case insensitive"


def test_whitespace_and_case_insensitive():
    """Test that whitespace handling works with case insensitive comparisons"""
    result1 = data_having("ROWS>100")
    result2 = data_having("rows > 100")
    result3 = data_having("  ROWS  >=  100  ")
    
    # Note: >= 100 includes = 100, so it might have more results than > 100
    assert len(result1) == len(result2), "Case and whitespace should not affect results"
    assert len(result3) >= len(result1), ">= should include >= results"
