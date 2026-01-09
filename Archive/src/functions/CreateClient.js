const { Connection } = require('tedious');

function createClient() {
  const config = {
    server: process.env.DB_SERVER,
    authentication: {
      type: 'default',
      options: {
        userName: process.env.DB_USER,
        password: process.env.DB_PASSWORD
      }
    },
    options: {
      database: process.env.DB_NAME,
      encrypt: true,
      trustServerCertificate: false,
      connectTimeout: 30000
    }
  };

  const connection = new Connection(config);

  connection.on('connect', function(err) {
    if (err) {
      console.error('Connection failed:', err);
    } else {
      console.log('Connected to Azure SQL Database');
    }
  });

  connection.on('error', function(err) {
    console.error('Connection error:', err);
  });

  return connection;
}

module.exports = { createClient };
