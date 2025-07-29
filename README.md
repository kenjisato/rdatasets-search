# R Datasets Search

A command-line tool for searching and exploring R datasets with interactive documentation and download capabilities.

## Installation

```bash
uv tool install git+https://github.com/kenjisato/rdatasets-search
```

## Usage

### Search datasets by data types and size

```bash
# Find datasets with binary columns
r-data having binary

# Find datasets with more than 100 rows
r-data having "rows > 100"

# Combine multiple filters
r-data having binary "rows > 100" numeric

# Find datasets with exactly 5 columns
r-data having "cols == 5"
```

### Interactive features

- **Pagination**: Navigate through results with `n` (next), `p` (previous), `g` (go to page)
- **Documentation**: Enter any dataset number to view detailed documentation
- **Download**: Press `d` in documentation view to download CSV data
- **Adaptive display**: Automatically adjusts to terminal size

### Filter options

**Data types**: `binary`, `character`, `factor`, `logical`, `numeric`

**Size filters**: `rows/cols` with operators `>`, `<`, `>=`, `<=`, `==`, `!=`

### Get help

```bash
r-data info
```

## Features

- 🔍 Flexible dataset filtering
- 📊 Interactive pagination with screen clearing
- 📖 Formatted documentation viewing
- 💾 CSV download with confirmation
- 📱 Responsive terminal display
- 🎯 Sequential dataset numbering for easy reference

## Example

```bash
$ r-data having binary "rows > 500"
Found 45 datasets matching the criteria:
Total datasets: 45
...

Page 1 of 2 (showing 1-30 of 45 results)
=====================================
┌─────┬─────────┬──────────┬─────────────────────┬──────┬──────┐
│ No. │ Package │ Item     │ Title               │ Rows │ Cols │
├─────┼─────────┼──────────┼─────────────────────┼──────┼──────┤
│ 1   │ AER     │ Affairs  │ Fair's Extramarital │ 601  │ 9    │
│     │         │          │ Affairs Data        │      │      │
└─────┴─────────┴──────────┴─────────────────────┴──────┴──────┘

Navigation: p) Previous page | n) Next page | q) Quit | g) Go to page | NUMBER) Show documentation

Enter your choice: 1
```

Enter a number to view documentation and download data!

## Development

### Running Tests

The project includes comprehensive tests using pytest. To run the tests:

```bash
# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests using uv
uv run pytest tests/ -v
```

### Test Structure

- `tests/test_data_having.py` - Core functionality tests
- `tests/test_case_insensitive_columns.py` - Case insensitive filtering tests  
- `tests/test_edge_cases.py` - Edge cases and error handling tests

All tests use proper pytest structure with 31 comprehensive test cases covering:
- Data type filtering (binary, character, numeric, factor, logical)
- Comparison operators (>, <, >=, <=, ==, !=)
- Case insensitive functionality
- Combined filters
- Edge cases and error handling
