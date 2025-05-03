import requests
import argparse
import os
import json # Moved import to top
from fastmcp import FastMCP, Client

mcp = FastMCP("Dolt Database Explorer")

# Configuration - you can adjust these as needed
DOLT_API_URL = "https://www.dolthub.com/api/v1alpha1"
DATABASE_OWNER = None # Set via --db argument
DATABASE_NAME = None # Set via --db argument
DATABASE_BRANCH = None # Set via --db argument
API_TOKEN = None

def get_dolt_query_url():
    """
Get the URL for executing SQL queries against the Dolt database
    """
    if not all([DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH]):
        raise ValueError("Database owner, name, and branch must be set via the --db argument.")
    return f"{DOLT_API_URL}/{DATABASE_OWNER}/{DATABASE_NAME}/{DATABASE_BRANCH}"

def get_auth_headers():
    """
Get headers with API token for authorized requests
    """
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = API_TOKEN
    return headers

@mcp.resource("schema://main")
def get_schema() -> str:
    """
Provide the database schema as a resource
    """
    try:
        # Query to get all tables
        tables_query = "SHOW TABLES"
        tables_response = requests.get(
            get_dolt_query_url(),
            params={"q": tables_query}
        )
        tables_response.raise_for_status()
        tables_data = tables_response.json()

        schema_parts = []

        # For each table, get its schema
        for row in tables_data.get("rows", []):
            # Extract table name from the row object based on JSON structure
            # Attempt to find the table name key dynamically
            table_name = None
            for key in row.keys():
                if key.startswith("Tables_in_"):
                    table_name = row[key]
                    break
            
            if not table_name and len(row) == 1: # Fallback for simpler API responses
                 table_name = list(row.values())[0]

            if table_name:
                # Get schema for this table
                schema_query = f"SHOW CREATE TABLE `{table_name}`"
                schema_response = requests.get(
                    get_dolt_query_url(),
                    params={"q": schema_query}
                )
                schema_response.raise_for_status()
                schema_data = schema_response.json()

                if schema_data.get("rows") and len(schema_data["rows"]) > 0:
                    # Extract Create Table statement from the response
                    create_statement = schema_data["rows"][0].get("Create Table")
                    if create_statement:
                        schema_parts.append(create_statement)

        return "\n\n".join(schema_parts)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"

@mcp.tool()
def read_query(sql: str) -> str:
    """
Execute SQL read queries safely on the Dolt database
    """
    try:
        # Execute the query
        response = requests.get(
            get_dolt_query_url(),
            params={"q": sql}
        )
        response.raise_for_status()
        result = response.json()

        # Format the result
        if "rows" not in result or not result["rows"]:
            return "No data returned or query doesn't return rows."

        # Get column names from the schema
        columns = result.get("schema", [])
        column_names = [col.get("columnName", f"Column{i}") for i, col in enumerate(columns)]

        # Create header row
        output = [" | ".join(column_names)]
        output.append("-" * len(" | ".join(column_names)))

        # Add data rows
        for row in result["rows"]:
            # Get values in the same order as column names
            row_values = []
            for col_name in column_names:
                val = row.get(col_name)
                row_values.append(str(val) if val is not None else "NULL")
            output.append(" | ".join(row_values))

        return "\n".join(output)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
def write_query(sql: str) -> str:
    """
Execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME) on the Dolt database. Handles polling for asynchronous operations.
"""
    try:
        # Check if API token is available
        if not API_TOKEN:
            return "Error: API token is required for write operations. Please start the server with --api-token parameter."
        
        # Verify this is a write operation
        sql_upper = sql.upper().strip()
        if not (sql_upper.startswith('INSERT') or
                sql_upper.startswith('UPDATE') or
                sql_upper.startswith('DELETE') or
                sql_upper.startswith('CREATE') or
                sql_upper.startswith('DROP') or
                sql_upper.startswith('ALTER') or
                sql_upper.startswith('RENAME')): # Added RENAME
            return "Error: This function only accepts write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME)" # Added RENAME to message
        
        # Set up headers with API token
        headers = get_auth_headers()
        
        # Execute the write query using POST request
        if not all([DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH]):
             return "Error: Database owner, name, and branch must be set via the --db argument."
        write_url = f"{DOLT_API_URL}/{DATABASE_OWNER}/{DATABASE_NAME}/write/{DATABASE_BRANCH}/{DATABASE_BRANCH}"
        
        # Use params instead of json
        response = requests.post(
            write_url,
            params={"q": sql},
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        # Check for errors in the response
        if "errors" in result and result["errors"]:
            return f"Error executing write query: {result['errors']}"
        
        # If we received an operation_name, poll for completion
        if "operation_name" in result:
            operation_name = result["operation_name"]
            
            # Define the polling function
            def get_operation(op_name):
                """Get the status of an operation by its name"""
                op_res = requests.get(
                    f"{DOLT_API_URL}/{DATABASE_OWNER}/{DATABASE_NAME}/write", # Base URL for operations
                    params={"operationName": op_name},
                    headers=headers
                )
                op_res.raise_for_status()
                return op_res.json()
            
            def poll_operation(op_name):
                """Poll an operation until it's done or max retries is reached"""
                done = False
                max_retries = 10
                retry_count = 0
                
                while not done and retry_count < max_retries:
                    poll_res = get_operation(op_name)
                    done = poll_res.get("done", False)
                    
                    if done:
                        return poll_res
                    else:
                        import time
                        time.sleep(3)  # Wait 3 seconds between polls
                        retry_count += 1
                
                # If we've reached max retries but the operation isn't done
                if retry_count >= max_retries:
                    return {"done": False, "max_retries_reached": True}
                
                return poll_res
            
            # Poll the operation
            poll_result = poll_operation(operation_name)
            
            if poll_result.get("max_retries_reached", False):
                return f"Write operation submitted (ID: {operation_name}), but is taking longer than expected to complete. It may still be processing."
            
            if poll_result.get("done", False):
                res_details = poll_result.get("res_details", {})
                query_status = res_details.get("query_execution_status")
                query_message = res_details.get("query_execution_message", "")
                
                # Add final commit step with empty query to finalize changes
                # Commit step uses the same write URL but with empty params
                commit_url = f"{DOLT_API_URL}/{DATABASE_OWNER}/{DATABASE_NAME}/write/{DATABASE_BRANCH}/{DATABASE_BRANCH}"
                merge_response = requests.post(
                    commit_url,
                    params=None,  # Empty query to finalize/commit changes
                    headers=headers
                )
                
                if merge_response.status_code == 200:
                    merge_result = merge_response.json()
                    if "operation_name" in merge_result:
                        # Poll the commit operation
                        commit_poll_result = poll_operation(merge_result["operation_name"])
                        if commit_poll_result.get("done", False):
                            return f"Write operation successful and committed: {query_message}"
                        else:
                            return f"Write operation successful but commit is still processing: {query_message}"
                    else:
                        return f"Write operation successful: {query_message}"
                else:
                    return f"Write operation successful but commit failed: {query_message}"
            
            return f"Write operation status unknown. Operation ID: {operation_name}"
        
        # For direct responses with rows_affected
        if "rows_affected" in result:
            return f"Success: {result['rows_affected']} row(s) affected"
            
        # Default success message
        return "Success: Query executed successfully"
            
    except Exception as e:
        return f"Error executing write query: {str(e)}"

@mcp.tool()
def list_tables() -> str:
    """
List the BASE tables in the database (excluding views)
    """
    try:
        # Use SHOW FULL TABLES to filter by Table_type
        query = "SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';"
        response = requests.get(
            get_dolt_query_url(),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return "No tables found."

        # Debug information
        debug_info = [
            "Debug information:",
            f"DATABASE_OWNER: {DATABASE_OWNER}",
            f"DATABASE_NAME: {DATABASE_NAME}",
            f"DATABASE_BRANCH: {DATABASE_BRANCH}",
            f"Expected column pattern: Tables_in_*"
        ]
        
        if result.get("rows") and len(result["rows"]) > 0:
            first_row = result["rows"][0]
            debug_info.append(f"Available keys in first row: {list(first_row.keys())}")
            
            # Add sample row data
            import json
            debug_info.append(f"Sample row: {json.dumps(first_row, indent=2)}")
        
        # Extract table names from the rows
        tables = []
        
        for row in result.get("rows", []):
            table_name = None
            # Look for a key starting with "Tables_in_"
            for key in row.keys():
                 if key.startswith("Tables_in_"):
                     table_name = row[key]
                     break
            
            # Fallback if only one column is returned (simpler API response)
            if not table_name and len(row) == 1:
                table_name = list(row.values())[0]

            if table_name:
                tables.append(str(table_name)) # Ensure it's a string

        # Add tables info to debug output
        debug_info.append(f"Extracted tables count: {len(tables)}")
        if tables:
            debug_info.append("First few tables: " + ", ".join(tables[:3]))
        
        # Print debug info to server console
        print("\n".join(debug_info))
        
        # Return the table list to the client
        return "\n".join(tables)
    except Exception as e:
        error_msg = f"Error listing tables: {str(e)}"
        print(error_msg)  # Print to server console for debugging
        return error_msg

@mcp.tool()
def describe_table(table_name: str) -> str:
    """
Describe the structure of a specific table. Handles table names that require quoting (e.g., containing spaces) automatically.
    """
    try:
        # Ensure table name is quoted correctly, especially if it contains spaces or special chars
        # The f-string with backticks handles this.
        response = requests.get(
            get_dolt_query_url(),
            params={"q": f"DESCRIBE `{table_name}`"}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return f"Table '{table_name}' not found or is empty."

        # Debug information
        debug_info = [
            f"Debug for describe_table({table_name}):",
            f"Result has {len(result.get('rows', []))} rows"
        ]
        
        if len(result.get("rows", [])) > 0:
            first_row = result["rows"][0]
            debug_info.append(f"Keys in first row: {list(first_row.keys())}")
            
            # Add sample row data
            import json
            debug_info.append(f"Sample row: {json.dumps(first_row, indent=2)}")
        
        # Print debug info to server console
        print("\n".join(debug_info))

        # Expected column names for DESCRIBE command
        expected_columns = ["Field", "Type", "Null", "Key", "Default", "Extra"]
        
        # Format the results
        output = [" | ".join(expected_columns)]
        output.append("-" * len(" | ".join(expected_columns)))

        # Add data rows
        for row in result["rows"]:
            # Map the row data to the expected columns
            row_values = []
            for col_name in expected_columns:
                val = row.get(col_name)
                row_values.append(str(val) if val is not None else "NULL")
            output.append(" | ".join(row_values))

        return "\n".join(output)
    except Exception as e:
        error_msg = f"Error describing table: {str(e)}"
        print(error_msg)  # Print to server console for debugging
        return error_msg

@mcp.tool()
def list_views() -> str:
    """
List the views in the database
    """
    try:
        # Use SHOW FULL TABLES to filter by Table_type
        query = "SHOW FULL TABLES WHERE Table_type = 'VIEW';"
        response = requests.get(
            get_dolt_query_url(),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            print("[list_views Debug] No views found in query result.") # Added debug
            return "No views found."

        views = []
        # SHOW FULL TABLES returns 'Tables_in_...' and 'Table_type' columns
        # Extract the view name from the 'Tables_in_...' column
        print(f"[list_views Debug] Processing {len(result.get('rows', []))} rows...") # Added debug
        for i, row in enumerate(result.get("rows", [])):
            view_name = None
            # Look for a key starting with "Tables_in_"
            for key in row.keys():
                 if key.startswith("Tables_in_"):
                     view_name = row[key]
                     break

            # Fallback if only one column is returned (less likely with SHOW FULL TABLES)
            if not view_name and len(row) == 1:
                view_name = list(row.values())[0]

            if view_name:
                views.append(str(view_name)) # Ensure it's a string
                print(f"[list_views Debug] Row {i}: Extracted view name: {view_name}") # Added debug
            else:
                print(f"[list_views Debug] Row {i}: Could not extract view name from row: {row}") # Added debug


        final_output = "\n".join(views)
        print(f"[list_views Debug] Final list of views: {views}") # Added debug
        print(f"[list_views Debug] Returning string:\n{final_output}") # Added debug
        return final_output # This already matches list_tables format

    except Exception as e:
        error_msg = f"Error listing views: {str(e)}"
        print(f"[list_views Error] {error_msg}") # Enhanced error logging
        return error_msg

@mcp.tool()
def describe_view(view_name: str) -> str:
    """
Show the CREATE VIEW statement for a specific view. Handles view names that require quoting (e.g., containing spaces) automatically.
    """
    try:
        # Ensure view name is quoted correctly
        query = f"SHOW CREATE VIEW `{view_name}`"
        response = requests.get(
            get_dolt_query_url(),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return f"View '{view_name}' not found or query failed."

        # Extract the 'Create View' statement
        # The exact key might vary slightly based on Dolt API version, adjust if needed
        create_statement = None
        if result["rows"]:
             row = result["rows"][0]
             # Common keys are 'Create View' or 'VIEW_DEFINITION'
             if "Create View" in row:
                 create_statement = row["Create View"]
             elif "VIEW_DEFINITION" in row: # Check alternative key
                 create_statement = row["VIEW_DEFINITION"]
             elif len(row) >= 2: # Fallback if keys are generic
                 # Assuming the definition is often the second column
                 create_statement = list(row.values())[1]


        if create_statement:
            return create_statement
        else:
            # Provide raw row data if specific key isn't found
            # import json # Removed local import
            return f"Could not extract view definition. Raw row data: {json.dumps(result['rows'][0])}"

    except Exception as e:
        return f"Error describing view '{view_name}': {str(e)}"

@mcp.tool()
def create_view(view_name: str, select_query: str) -> str:
    """
Create a new view in the database using the provided SELECT query. Handles view names that require quoting (e.g., containing spaces) automatically. Uses the write_query tool for execution.
    """
    # Basic validation
    if not view_name or not select_query:
        return "Error: Both view_name and select_query are required."
    if not select_query.upper().strip().startswith("SELECT"):
         return "Error: select_query must start with SELECT."

    sql = f"CREATE VIEW `{view_name}` AS {select_query}"
    # Use the existing write_query tool to handle execution, auth, and polling
    return write_query(sql)

@mcp.tool()
def drop_view(view_name: str) -> str:
    """
 Drop a view from the database. Handles view names that require quoting (e.g., containing spaces) automatically. Uses the write_query tool for execution.
    """
    if not view_name:
        return "Error: view_name is required."

    # Ensure view name is quoted correctly
    sql = f"DROP VIEW IF EXISTS `{view_name}`"
    # Use the existing write_query tool
    return write_query(sql)

# This content is removed as it was moved above
@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def get_current_database() -> str:
    """
    Return the currently configured database connection string in user/database/branch format.
    """
    if all([DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH]):
        return f"{DATABASE_OWNER}/{DATABASE_NAME}/{DATABASE_BRANCH}"
    else:
        # This case should ideally not happen if the server started correctly
        return "Error: Database details are not fully configured."
@mcp.tool()
def set_current_database(db_string: str) -> str:
    """
    Set the active database connection string. Expects format: user/database/branch.
    """
    global DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH
    try:
        parts = db_string.split('/')
        if len(parts) != 3:
            raise ValueError("Invalid format. Expected user/database/branch")
        
        # Basic validation (can be expanded if needed)
        owner, name, branch = parts
        if not owner or not name or not branch:
             raise ValueError("Database owner, name, and branch cannot be empty.")

        DATABASE_OWNER = owner
        DATABASE_NAME = name
        DATABASE_BRANCH = branch
        
        # Optionally, you might want to test the connection here or clear cached schema etc.
        
        return f"Database successfully set to: {db_string}"
    except ValueError as e:
        return f"Error setting database: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
def main():
    global DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH, API_TOKEN
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Dolt Database Explorer MCP Server')
    parser.add_argument('--db', required=False, help='Database connection string in format: user/database/branch (default: calvinw/coffee-shop/main)') # Explicitly not required
    parser.add_argument('--api-token', help='API token for write operations')
    
    args = parser.parse_args()
    
    # Determine the DB string to use (provided or default)
    db_string_to_use = args.db if args.db else 'calvinw/coffee-shop/main' # Handle default manually

    # Parse the database string
    try:
        db_parts = db_string_to_use.split('/') # Use the determined string
        if len(db_parts) != 3:
            # This should ideally not happen with the default, but good practice to keep validation
            raise ValueError(f"Invalid format for database string '{db_string_to_use}'. Expected user/database/branch")
        DATABASE_OWNER, DATABASE_NAME, DATABASE_BRANCH = db_parts
    except ValueError as e:
        print(f"Error parsing database string: {e}")
        exit(1)

    # Update API token if provided
    if args.api_token:
        API_TOKEN = args.api_token
    
    # The check below is removed as the parsing logic now handles the default value correctly.
    # The program will exit earlier if parsing fails.

    print("Dolt Database Explorer MCP Server is running")
    print(f"Connected to: {DATABASE_OWNER}/{DATABASE_NAME}, branch: {DATABASE_BRANCH}")
    print(f"API Token: {'Configured' if API_TOKEN else 'Not configured (read-only)'}")
    mcp.run()
