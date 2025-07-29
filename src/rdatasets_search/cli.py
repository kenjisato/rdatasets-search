import typer
import polars as pl
from typing import List
from .search import data_having
import sys
import shutil
import requests
from bs4 import BeautifulSoup, Tag
import re
import os

app = typer.Typer(help="R Datasets Search CLI")

def format_dataframe_output(df: pl.DataFrame) -> str:
    """
    Format Polars DataFrame for better CLI output without truncation
    """
    # Get terminal width, with max of 100 and fallback to 80
    try:
        terminal_width = shutil.get_terminal_size().columns
        table_width = min(terminal_width, 100)
    except:
        table_width = 80
    
    # Configure Polars to show more rows and columns
    with pl.Config(
        tbl_rows=-1,  # Show all rows
        tbl_cols=-1,  # Show all columns
        tbl_width_chars=table_width,  # Adaptive table width
        fmt_str_lengths=50,  # Longer string display
        tbl_hide_column_data_types=True,  # Hide data types like str/i64
        tbl_hide_dataframe_shape=True,  # Hide shape info like (30, 5)
    ):
        return str(df)

def fetch_documentation(doc_url: str) -> str:
    """
    Fetch and format documentation from the given URL
    """
    try:
        response = requests.get(doc_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Documentation"
        
        # Remove " R Documentation" suffix if present
        title_text = re.sub(r'\s*R Documentation$', '', title_text)
        
        # Extract main content
        main_content = soup.find('div', {'id': 'main'}) or soup.find('div', class_='main') or soup.body
        
        if not main_content:
            return f"Title: {title_text}\nURL: {doc_url}\n\nCould not extract main content from the documentation."
        
        # Remove script and style elements
        if main_content and isinstance(main_content, Tag):
            for script in main_content.find_all(["script", "style"]):
                script.decompose()
        
        result = f"Title: {title_text}\nURL: {doc_url}\n\n"
        
        # Extract description section
        description_section = main_content.find('h3', string='Description')
        if description_section:
            desc_content = []
            for sibling in description_section.find_next_siblings():
                if sibling.name == 'h3':
                    break
                if sibling.name == 'p':
                    desc_content.append(sibling.get_text().strip())
            if desc_content:
                result += '\n'.join(desc_content) + '\n\n'
        
        # Extract format/variables section
        format_section = main_content.find('h3', string='Format') or main_content.find('h3', string='Variables')
        if format_section:
            result += "## Variables\n\n"
            
            # Get description before the definition list
            format_desc = []
            for sibling in format_section.find_next_siblings():
                if sibling.name == 'h3':
                    break
                if sibling.name == 'p':
                    format_desc.append(sibling.get_text().strip())
                elif sibling.name == 'dl':
                    break
            
            if format_desc:
                result += '\n'.join(format_desc) + '\n\n'
            
            # Extract definition list (dt/dd pairs)
            dl = format_section.find_next_sibling('dl')
            if not dl:
                # Look for dl in subsequent siblings
                for sibling in format_section.find_next_siblings():
                    if sibling.name == 'dl':
                        dl = sibling
                        break
                    elif sibling.name == 'h3':
                        break
            
            if dl:
                dt_elements = dl.find_all('dt')
                dd_elements = dl.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    dt_text = dt.get_text().strip()
                    dd_text = dd.get_text().strip()
                    result += f"{dt_text} : {dd_text}\n"
        
        # Limit total length
        if len(result) > 3000:
            result = result[:3000] + "...\n\n[Content truncated - visit URL for full documentation]"
        
        return result
        
    except requests.RequestException as e:
        return f"Error fetching documentation: {e}\nURL: {doc_url}"
    except Exception as e:
        return f"Error parsing documentation: {e}\nURL: {doc_url}"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def download_dataset(csv_url: str, dataset_name: str) -> bool:
    """Download dataset from CSV URL to current directory"""
    try:
        # Ask for confirmation
        response = input(f"Download {dataset_name}.csv to current directory? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            typer.echo("Download cancelled.")
            return False
        
        # Download the file
        typer.echo(f"Downloading {dataset_name}.csv...")
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Save to current directory
        filename = f"{dataset_name}.csv"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        typer.echo(f"Successfully downloaded {filename}")
        return True
        
    except requests.RequestException as e:
        typer.echo(f"Error downloading file: {e}")
        return False
    except Exception as e:
        typer.echo(f"Error saving file: {e}")
        return False

def display_documentation_with_navigation(doc_content: str, dataset_num: int, original_df: pl.DataFrame):
    """Display documentation with navigation back to table"""
    while True:
        clear_screen()
        
        # Get terminal width for separator lines
        try:
            terminal_width = shutil.get_terminal_size().columns
            separator_width = min(terminal_width, 80)
        except:
            separator_width = 80
        
        typer.echo(f"Documentation for dataset #{dataset_num}")
        typer.echo("=" * separator_width)
        typer.echo(doc_content)
        typer.echo("\n" + "=" * separator_width)
        typer.echo("Navigation: b) Back to table | d) Download CSV | q) Quit")
        
        try:
            choice = input("\nEnter your choice: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return 'q'
        
        if choice == 'b':
            return 'back'
        elif choice == 'q':
            return 'q'
        elif choice == 'd':
            # Get dataset info for download
            dataset_row = original_df.row(dataset_num - 1, named=True)
            csv_url = dataset_row["CSV"]
            package_name = dataset_row["Package"]
            item_name = dataset_row["Item"]
            dataset_name = f"{package_name}_{item_name}"
            
            # Download the dataset
            download_success = download_dataset(csv_url, dataset_name)
            if download_success:
                input("Press Enter to continue...")
            else:
                input("Press Enter to continue...")
        else:
            typer.echo("Invalid choice. Press 'b' to go back, 'd' to download, or 'q' to quit.")
            input("Press Enter to continue...")

def paginate_results(df: pl.DataFrame, original_df: pl.DataFrame, page_size: int | None = None):
    """
    Display results with pagination using screen clearing like less
    """
    # Calculate adaptive page size based on terminal height
    if page_size is None:
        try:
            terminal_height = shutil.get_terminal_size().lines
            # Reserve space for header (3 lines), navigation (4 lines), and some buffer (3 lines)
            available_lines = terminal_height - 10
            # Minimum 10 rows, maximum 30 rows
            page_size = max(10, min(available_lines, 30))
        except:
            page_size = 30  # fallback
    
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size
    current_page = 1
    
    while True:
        # Clear screen and display current page
        clear_screen()
        
        # Calculate start and end indices for current page
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        # Get current page data and add row numbers
        page_data = df.slice(start_idx, page_size)
        
        # Add sequential row numbers starting from the global position
        page_data_with_numbers = page_data.with_columns([
            pl.Series("No.", range(start_idx + 1, start_idx + len(page_data) + 1))
        ]).select([
            "No.", "Package", "Item", "Title", "Rows", "Cols"
        ])
        
        # Get terminal width for separator lines
        try:
            terminal_width = shutil.get_terminal_size().columns
            separator_width = min(terminal_width, 80)
        except:
            separator_width = 80
        
        # Display page header
        typer.echo(f"Page {current_page} of {total_pages} (showing {start_idx + 1}-{end_idx} of {total_rows} results)")
        typer.echo("=" * separator_width)
        
        # Display the data
        formatted_output = format_dataframe_output(page_data_with_numbers)
        typer.echo(formatted_output)
        
        # Display navigation options
        typer.echo("\n" + "=" * separator_width)
        nav_options = []
        if current_page > 1:
            nav_options.append("p) Previous page")
        if current_page < total_pages:
            nav_options.append("n) Next page")
        nav_options.extend(["q) Quit", "g) Go to page", "NUMBER) Show documentation"])
        
        typer.echo("Navigation: " + " | ".join(nav_options))
        
        # Get user input
        try:
            choice = input("\nEnter your choice: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nExiting...")
            break
        
        if choice == 'q':
            break
        elif choice == 'n' and current_page < total_pages:
            current_page += 1
        elif choice == 'p' and current_page > 1:
            current_page -= 1
        elif choice == 'g':
            try:
                page_num = int(input(f"Enter page number (1-{total_pages}): "))
                if 1 <= page_num <= total_pages:
                    current_page = page_num
                else:
                    typer.echo(f"Invalid page number. Please enter a number between 1 and {total_pages}.")
                    input("Press Enter to continue...")
            except ValueError:
                typer.echo("Invalid input. Please enter a valid page number.")
                input("Press Enter to continue...")
        elif choice.isdigit():
            # User entered a number to view documentation
            row_num = int(choice)
            if 1 <= row_num <= len(original_df):
                # Get the documentation URL for this row
                doc_url = original_df.row(row_num - 1, named=True)["Doc"]
                
                # Show loading message
                clear_screen()
                typer.echo(f"Fetching documentation for dataset #{row_num}...")
                typer.echo("=" * separator_width)
                
                # Fetch and display documentation
                doc_content = fetch_documentation(doc_url)
                
                # Display documentation with navigation
                nav_result = display_documentation_with_navigation(doc_content, row_num, original_df)
                if nav_result == 'q':
                    break
                # If nav_result == 'back', continue to show the table
            else:
                typer.echo(f"Invalid dataset number. Please enter a number between 1 and {len(original_df)}.")
                input("Press Enter to continue...")
        else:
            typer.echo("Invalid choice. Please try again.")
            input("Press Enter to continue...")

@app.command()
def having(
    filters: List[str] = typer.Argument(..., help="Filter arguments (e.g., 'binary', 'rows > 100')")
):
    """
    Filter R datasets based on data types and size criteria.
    
    Examples:
    
    r-data having binary
    
    r-data having "rows > 100"
    
    r-data having binary "rows > 100" numeric
    
    r-data having "cols == 5" character
    """
    try:
        # Call the data_having function with the provided filters
        result = data_having(*filters)
        
        if len(result) == 0:
            typer.echo("No datasets found matching the specified criteria.")
            return
        
        # Hide CSV, Doc, and n_* columns from display
        display_result = result.select([
            "Package", "Item", "Title", "Rows", "Cols"
        ])
        
        # Display summary
        typer.echo(f"Found {len(result)} datasets matching the criteria:")
        
        # Show some basic statistics
        total_rows = result.select(pl.col("Rows").sum()).item()
        avg_rows = result.select(pl.col("Rows").mean()).item()
        total_cols = result.select(pl.col("Cols").sum()).item()
        avg_cols = result.select(pl.col("Cols").mean()).item()
        
        typer.echo(f"Total datasets: {len(result)}")
        typer.echo(f"Total rows across all datasets: {total_rows:,}")
        typer.echo(f"Average rows per dataset: {avg_rows:.1f}")
        typer.echo(f"Total columns across all datasets: {total_cols:,}")
        typer.echo(f"Average columns per dataset: {avg_cols:.1f}")
        
        # Use pagination to display results
        paginate_results(display_result, result)
        
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def info():
    """
    Show information about available filter options.
    """
    typer.echo("R Datasets Search - Filter Options")
    typer.echo("=" * 40)
    
    typer.echo("\n📊 Data Type Filters:")
    typer.echo("  binary     - Datasets with binary/boolean columns")
    typer.echo("  character  - Datasets with character/string columns")
    typer.echo("  factor     - Datasets with factor/categorical columns")
    typer.echo("  logical    - Datasets with logical/boolean columns")
    typer.echo("  numeric    - Datasets with numeric columns")
    
    typer.echo("\n📏 Size Filters:")
    typer.echo("  rows > N   - Datasets with more than N rows")
    typer.echo("  rows < N   - Datasets with fewer than N rows")
    typer.echo("  rows >= N  - Datasets with N or more rows")
    typer.echo("  rows <= N  - Datasets with N or fewer rows")
    typer.echo("  rows == N  - Datasets with exactly N rows")
    typer.echo("  rows != N  - Datasets with not exactly N rows")
    typer.echo("  cols > N   - Datasets with more than N columns")
    typer.echo("  cols < N   - Datasets with fewer than N columns")
    typer.echo("  cols >= N  - Datasets with N or more columns")
    typer.echo("  cols <= N  - Datasets with N or fewer columns")
    typer.echo("  cols == N  - Datasets with exactly N columns")
    typer.echo("  cols != N  - Datasets with not exactly N columns")
    
    typer.echo("\n💡 Notes:")
    typer.echo("  - All arguments are case-insensitive")
    typer.echo("  - Whitespace around operators is flexible")
    typer.echo("  - Multiple filters can be combined")
    typer.echo("  - Use quotes around expressions with spaces")
    
    typer.echo("\n🔍 Examples:")
    typer.echo("  r-data having binary")
    typer.echo("  r-data having \"rows > 100\"")
    typer.echo("  r-data having binary \"rows > 100\" numeric")
    typer.echo("  r-data having \"cols == 5\" character")

if __name__ == "__main__":
    app()
