import pyodbc
import struct
import os
from typing import Optional, Sequence, Any
from azure.identity import DefaultAzureCredential


def get_db_connection():
    """Create an Azure SQL connection using Managed Identity (no password)."""
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_NAME")

    if not server or not database:
        raise ValueError("DB_SERVER and DB_NAME environment variables must be set")

    # Acquire token for Azure SQL
    credential = DefaultAzureCredential()
    raw_token = credential.get_token("https://database.windows.net/.default")
    encoded_token: bytes = raw_token.token.encode("utf-16-le")
    token_struct = struct.pack(f'<I{len(encoded_token)}s', len(encoded_token), encoded_token)

    # Use ODBC Driver 18 (common on Linux runners)
    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

    SQL_COPT_SS_ACCESS_TOKEN = 1256
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


def execute_query(query: str, params: Optional[Sequence[Any]] = None):
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
