import pyodbc
import struct
import os
from azure.identity import DefaultAzureCredential


def get_db_connection():
    """
    Get a secure connection to Azure SQL Database using Managed Identity.
    
    This approach:
    - Uses DefaultAzureCredential (no password needed!)
    - Works with Azure Functions Managed Identity
    - Requires MSI to be enabled on the Function App
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Raises:
        Exception: If token retrieval or connection fails
    """
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    
    if not server or not database:
        raise ValueError('DB_SERVER and DB_NAME environment variables must be set')
    
    try:
        # 1. Get a token for Azure SQL using Managed Identity
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/.default").token
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

        # 2. Setup connection string (no password needed!)
        # Driver 18 is the latest; use Driver 17 if 18 is not available on your host
        conn_str = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        
        # 3. Connect and inject the token for authentication
        SQL_COPT_SS_ACCESS_TOKEN = 1256  # Connection option for access tokens
        conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
        
        return conn
        
    except Exception as e:
        raise Exception(f'Failed to establish database connection: {str(e)}')


def execute_query(query: str, params: list = None):
    """
    Execute a SQL query securely with parameters.
    
    Args:
        query (str): SQL query string with ? placeholders for parameters
        params (list): List of parameter values to bind to the query
        
    Returns:
        list or dict: Results for SELECT queries or row count for INSERT/UPDATE/DELETE
        
    Raises:
        Exception: If query execution fails
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute with parameters for security (prevents SQL injection)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle SELECT vs write operations
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            # Convert to list of dicts for JSON serialization
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            # For INSERT/UPDATE/DELETE, commit and return row count
            conn.commit()
            return {'rows_affected': cursor.rowcount}
            
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise Exception(f'Database error: {str(e)}')
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f'Error executing query: {str(e)}')
    finally:
        if conn:
            conn.close()
