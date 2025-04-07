const mysql = require('mysql2/promise');

function createDBConnection({ database }) {
  return mysql.createPool({
    host: 'localhost',
    user: 'root', 
    password: '', 
    database: database,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
  });
}

module.exports = createDBConnection;
