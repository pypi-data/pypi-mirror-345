<?php

declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '1');

// Load environment variables from .env file
if (file_exists(__DIR__ . '/../.env')) {
    $envFile = file_get_contents(__DIR__ . '/../.env');
    $lines = explode("\n", $envFile);

    foreach ($lines as $line) {
        if (empty($line) || strpos($line, '#') === 0) {
            continue;
        }

        list($key, $value) = explode('=', $line, 2) + [null, null];

        if ($key && $value) {
            $key = trim($key);
            $value = trim($value);

            // Only set from .env if not already defined in the environment
            // This ensures container environment variables take precedence
            if (!isset($_ENV[$key]) && !getenv($key)) {
                $_ENV[$key] = $value;
                putenv("$key=$value");
            }
        }
    }
}

// Get database port - ensure we use the internal container port for connections inside Docker
// For MariaDB/MySQL, host port might be different (e.g., 3307) but container port should be 3306
if (isset($_ENV['DB_ENGINE']) && ($_ENV['DB_ENGINE'] === 'mariadb' || $_ENV['DB_ENGINE'] === 'mysql')) {
    if (isset($_ENV['DB_PORT']) && $_ENV['DB_PORT'] !== '3306') {
        // If we're inside a Docker container, always use 3306 for internal connections
        if (file_exists('/.dockerenv')) {
            $_ENV['DB_PORT'] = '3306';
            putenv('DB_PORT=3306');
        }
    }
}

// Force DB_PORT to be 3306 inside Docker containers when connecting to MySQL/MariaDB
// This ensures the correct internal port is used regardless of external port mapping
if (file_exists('/.dockerenv')) {
    if (isset($_ENV['DB_ENGINE'])) {
        if ($_ENV['DB_ENGINE'] === 'mariadb' || $_ENV['DB_ENGINE'] === 'mysql') {
            // Inside Docker, always use 3306 for internal MySQL/MariaDB connections
            $_ENV['DB_PORT'] = '3306';
            putenv('DB_PORT=3306');
        } elseif ($_ENV['DB_ENGINE'] === 'postgresql') {
            // Inside Docker, always use 5432 for internal PostgreSQL connections
            $_ENV['DB_PORT'] = '5432';
            putenv('DB_PORT=5432');
        }
    }
}

spl_autoload_register(function ($class) {
    $file = __DIR__ . DIRECTORY_SEPARATOR .
        str_replace(['\\', '/'], DIRECTORY_SEPARATOR, $class) . '.php';

    if (file_exists($file)) {
        require_once $file;
        return true;
    }
    return false;
});

$composerAutoloader = __DIR__ . '/../vendor/autoload.php';
if (file_exists($composerAutoloader)) {
    require_once $composerAutoloader;
}
