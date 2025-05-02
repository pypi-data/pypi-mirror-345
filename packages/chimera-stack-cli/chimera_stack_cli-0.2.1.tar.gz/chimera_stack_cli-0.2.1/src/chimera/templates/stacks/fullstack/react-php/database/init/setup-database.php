<?php

/**
 * Database setup script for ChimeraStack
 *
 * This file handles database connection setup for different database types.
 * It should be included in your application's bootstrap process.
 */

// Determine database type from environment variables
$dbConnection = getenv('DB_CONNECTION') ?: 'mysql';

// Override the DB_PORT based on database type
if ($dbConnection === 'postgresql') {
    // For PostgreSQL, use port 5432
    putenv('DB_PORT=5432');
    // Update .env file if it exists
    if (file_exists(dirname(__DIR__) . '/.env')) {
        $envContent = file_get_contents(dirname(__DIR__) . '/.env');
        $envContent = preg_replace('/DB_PORT=\d+/', 'DB_PORT=5432', $envContent);
        file_put_contents(dirname(__DIR__) . '/.env', $envContent);
    }
} else {
    // For MySQL/MariaDB, use port 3306
    putenv('DB_PORT=3306');
    // Update .env file if it exists
    if (file_exists(dirname(__DIR__) . '/.env')) {
        $envContent = file_get_contents(dirname(__DIR__) . '/.env');
        $envContent = preg_replace('/DB_PORT=\d+/', 'DB_PORT=3306', $envContent);
        file_put_contents(dirname(__DIR__) . '/.env', $envContent);
    }
}

// Display connection information for debugging
echo "Database setup completed:\n";
echo "Connection: " . $dbConnection . "\n";
echo "Host: " . getenv('DB_HOST') . "\n";
echo "Port: " . getenv('DB_PORT') . "\n";
echo "Database: " . getenv('DB_DATABASE') . "\n";
echo "Username: " . getenv('DB_USERNAME') . "\n";

// Return an array with the database configuration
return [
    'connection' => $dbConnection,
    'host' => getenv('DB_HOST'),
    'port' => getenv('DB_PORT'),
    'database' => getenv('DB_DATABASE'),
    'username' => getenv('DB_USERNAME'),
    'password' => getenv('DB_PASSWORD'),
];
