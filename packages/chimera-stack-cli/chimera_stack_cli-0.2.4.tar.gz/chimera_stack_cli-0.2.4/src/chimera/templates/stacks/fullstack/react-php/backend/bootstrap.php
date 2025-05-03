<?php

/**
 * Bootstrap file for the ChimeraStack React-PHP template
 * This file handles database setup and environment configuration
 */

// Load environment variables
$dotenv = __DIR__ . '/.env';
if (file_exists($dotenv)) {
    $lines = file($dotenv, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false && strpos($line, '#') !== 0) {
            list($key, $value) = explode('=', $line, 2);
            $key = trim($key);
            $value = trim($value);
            if (!empty($key)) {
                putenv("$key=$value");
            }
        }
    }
}

// Get database connection type (from docker environment or .env)
$dbConnection = getenv('DB_CONNECTION') ?: 'mysql';

// Set correct internal port for different database types
$dbPort = '3306'; // Default to MySQL port
if ($dbConnection === 'pgsql') {
    $dbPort = '5432'; // Use PostgreSQL port
    putenv('DB_PORT=5432');
} else {
    putenv('DB_PORT=3306');
}

// Database connection parameters
$dbParams = [
    'connection' => $dbConnection,
    'host' => getenv('DB_HOST') ?: 'db',
    'port' => getenv('DB_PORT') ?: $dbPort,
    'database' => getenv('DB_DATABASE'),
    'username' => getenv('DB_USERNAME'),
    'password' => getenv('DB_PASSWORD'),
];

// Display the current database configuration
if (PHP_SAPI === 'cli') {
    echo "Database configuration:\n";
    echo "Connection: {$dbParams['connection']}\n";
    echo "Host: {$dbParams['host']}\n";
    echo "Port: {$dbParams['port']}\n";
    echo "Database: {$dbParams['database']}\n";
    echo "Username: {$dbParams['username']}\n";
}

return $dbParams;
