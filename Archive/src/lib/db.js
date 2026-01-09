const { Connection, Request } = require('tedious');

const config = {
  server: process.env.DB_SERVER,
  authentication: {
    type: 'azure-active-directory-msi-app-service'
  },
  options: {
    database: process.env.DB_NAME,
    encrypt: true, // Required for Azure SQL
    trustServerCertificate: false
  }
};

async function executeQuery(query, params = []) {
  return new Promise((resolve, reject) => {
    const connection = new Connection(config);
    connection.on('connect', err => {
      if (err) return reject(err);
      
      const request = new Request(query, (err, rowCount, rows) => {
        connection.close();
        if (err) return reject(err);
        resolve(rows);
      });

      // Parameterized queries (Security-First)
      params.forEach(p => request.addParameter(p.name, p.type, p.value));
      connection.execSql(request);
    });
    connection.connect();
  });
}

async function auditLog(userId, action, details = {}) {
  const logQuery = `
    INSERT INTO AuditLogs (UserId, Action, Details, Timestamp)
    VALUES (@userId, @action, @details, @timestamp)
  `;
  
  try {
    await executeQuery(logQuery, [
      { name: 'userId', type: require('tedious').TYPES.NVarChar, value: userId },
      { name: 'action', type: require('tedious').TYPES.NVarChar, value: action },
      { name: 'details', type: require('tedious').TYPES.NVarChar, value: JSON.stringify(details) },
      { name: 'timestamp', type: require('tedious').TYPES.DateTime2, value: new Date() }
    ]);
  } catch (error) {
    console.error('Audit logging failed:', error.message);
    // Fail silently - audit failures should not block main operation
  }
}

module.exports = { executeQuery, auditLog };
