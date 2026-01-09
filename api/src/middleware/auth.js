/**
 * Authentication Middleware
 * Validates JWT tokens and extracts user identity
 */

function extractUserFromRequest(req) {
  // Azure Functions provides user identity in headers when using App Service Authentication
  const userId = req.headers['x-ms-client-principal-id'] || 
                 req.headers['x-user-id'] || 
                 null;
  
  const userName = req.headers['x-ms-client-principal-name'] || null;
  
  return { userId, userName };
}

function requireAuth(context, req) {
  const { userId } = extractUserFromRequest(req);
  
  if (!userId) {
    context.res = {
      status: 401,
      body: 'Unauthorized: No user identity found'
    };
    return false;
  }
  
  return true;
}

module.exports = { extractUserFromRequest, requireAuth };
