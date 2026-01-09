import azure.functions as func
import pyodbc
import json
import os
from datetime import datetime
from azure.identity import DefaultAzureCredential

# Initialize Azure Functions app
app = func.FunctionApp()

# Database configuration
DB_SERVER = os.getenv('DB_SERVER')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Build connection string
CONNECTION_STRING = (
    f'Driver={{ODBC Driver 17 for SQL Server}};'
    f'Server=tcp:{DB_SERVER},1433;'
    f'Database={DB_NAME};'
    f'Uid={DB_USER};'
    f'Pwd={DB_PASSWORD};'
    f'Encrypt=yes;'
    f'TrustServerCertificate=no;'
    f'Connection Timeout=30;'
)


def extract_user_from_request(req: func.HttpRequest):
    """
    Authentication Helper
    Extracts user identity from Azure App Service authentication headers
    """
    user_id = req.headers.get('X-MS-CLIENT-PRINCIPAL-ID') or req.headers.get('X-User-ID')
    user_name = req.headers.get('X-MS-CLIENT-PRINCIPAL-NAME')
    
    return {'user_id': user_id, 'user_name': user_name}


def require_auth(req: func.HttpRequest):
    """
    Authentication Middleware
    Validates that user is authenticated
    """
    user = extract_user_from_request(req)
    
    if not user['user_id']:
        return False, 'Unauthorized: No user identity found'
    
    return True, user


def execute_query(query: str, params: list = None):
    """
    Execute a SQL query and return results
    Uses pyodbc for secure parameterized queries
    """
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Fetch all results if SELECT
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            # Convert to list of dicts
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            conn.close()
            return results
        else:
            # For INSERT/UPDATE/DELETE, commit and return row count
            conn.commit()
            row_count = cursor.rowcount
            conn.close()
            return {'rows_affected': row_count}
            
    except pyodbc.Error as e:
        raise Exception(f'Database error: {str(e)}')
    except Exception as e:
        raise Exception(f'Error executing query: {str(e)}')


def audit_log(user_id: str, action: str, details: dict = None):
    """
    Log audit events to the AuditLogs table
    Fail silently if audit logging fails
    """
    log_query = """
    INSERT INTO AuditLogs (UserId, Action, Details, Timestamp)
    VALUES (?, ?, ?, ?)
    """
    
    try:
        details_json = json.dumps(details or {})
        execute_query(log_query, [user_id, action, details_json, datetime.now()])
    except Exception as e:
        # Log to console but don't fail the main operation
        print(f'Audit logging failed: {str(e)}')


@app.function_name('CreateClient')
@app.route(route='clients', methods=['POST'], auth_level=func.AuthLevel.ANONYMOUS)
def create_client(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger to create a new client record
    Requires authentication and valid client data
    """
    # Authentication check
    is_authenticated, auth_response = require_auth(req)
    if not is_authenticated:
        return func.HttpResponse(auth_response, status_code=401)
    
    user = extract_user_from_request(req)
    
    try:
        # Parse request body
        req_body = req.get_json()
        client_name = req_body.get('name')
        client_email = req_body.get('email')
        
        if not client_name or not client_email:
            return func.HttpResponse(
                json.dumps({'error': 'Missing required fields: name, email'}),
                status_code=400,
                mimetype='application/json'
            )
        
        # Insert client record
        insert_query = """
        INSERT INTO Clients (Name, Email, CreatedBy, CreatedAt)
        VALUES (?, ?, ?, ?)
        """
        
        result = execute_query(insert_query, [client_name, client_email, user['user_id'], datetime.now()])
        
        # Audit log the creation
        audit_log(user['user_id'], 'CREATE_CLIENT', {
            'client_name': client_name,
            'client_email': client_email
        })
        
        return func.HttpResponse(
            json.dumps({
                'message': 'Client created successfully',
                'data': {'name': client_name, 'email': client_email}
            }),
            status_code=201,
            mimetype='application/json'
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name('GetClients')
@app.route(route='clients', methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)
def get_clients(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger to retrieve all clients
    Requires authentication
    """
    is_authenticated, auth_response = require_auth(req)
    if not is_authenticated:
        return func.HttpResponse(auth_response, status_code=401)
    
    user = extract_user_from_request(req)
    
    try:
        # Fetch all clients
        select_query = "SELECT * FROM Clients ORDER BY CreatedAt DESC"
        clients = execute_query(select_query)
        
        # Audit log the query
        audit_log(user['user_id'], 'GET_CLIENTS', {'record_count': len(clients)})
        
        return func.HttpResponse(
            json.dumps({'data': clients, 'count': len(clients)}),
            status_code=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
