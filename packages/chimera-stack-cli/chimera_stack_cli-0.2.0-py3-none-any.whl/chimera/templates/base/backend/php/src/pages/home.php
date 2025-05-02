<?php

declare(strict_types=1);
require_once __DIR__ . '/../Database.php';

$title = 'ChimeraStack PHP Development Environment';
$webPort = $_ENV['NGINX_PORT'] ?? $_ENV['WEB_PORT'] ?? '8080';
$dbEngine = $_ENV['DB_ENGINE'] ?? 'mysql';

// Set ports based on database engine
if ($dbEngine === 'postgresql') {
    $dbPort = $_ENV['DB_PORT'] ?? $_ENV['POSTGRES_PORT'] ?? '5432';
    $adminPort = $_ENV['PGADMIN_PORT'] ?? $_ENV['ADMIN_PORT'] ?? '8080';
    $dbTypeName = 'PostgreSQL';
    $adminToolName = 'pgAdmin';
} elseif ($dbEngine === 'mariadb') {
    $dbPort = $_ENV['DB_PORT'] ?? $_ENV['MARIADB_PORT'] ?? '3306';
    $adminPort = $_ENV['PHPMYADMIN_PORT'] ?? $_ENV['ADMIN_PORT'] ?? '8080';
    $dbTypeName = 'MariaDB';
    $adminToolName = 'phpMyAdmin';
} else {
    // MySQL default
    $dbPort = $_ENV['DB_PORT'] ?? $_ENV['MYSQL_PORT'] ?? '3306';
    $adminPort = $_ENV['PHPMYADMIN_PORT'] ?? $_ENV['ADMIN_PORT'] ?? '8080';
    $dbTypeName = 'MySQL';
    $adminToolName = 'phpMyAdmin';
}

$dbHost = $_ENV['DB_HOST'] ?? $dbEngine;

// Get database connection info
$db = Database::getInstance();
$connectionInfo = $db->getConnectionInfo();

// For diagnostic purposes
$dbDiagnostics = [
    'DB_HOST' => $_ENV['DB_HOST'] ?? getenv('DB_HOST') ?? 'not set',
    'DB_ENGINE' => $_ENV['DB_ENGINE'] ?? getenv('DB_ENGINE') ?? 'not set',
    'DB_DATABASE' => $_ENV['DB_DATABASE'] ?? getenv('DB_DATABASE') ?? 'not set',
    'DB_USERNAME' => $_ENV['DB_USERNAME'] ?? getenv('DB_USERNAME') ?? 'not set',
    'DB_PORT' => $_ENV['DB_PORT'] ?? getenv('DB_PORT') ?? 'not set',
    'ADMIN_PORT' => $_ENV['ADMIN_PORT'] ?? getenv('ADMIN_PORT') ?? 'not set'
];

if ($dbEngine === 'postgresql') {
    $dbDiagnostics['POSTGRES_PORT'] = $_ENV['POSTGRES_PORT'] ?? getenv('POSTGRES_PORT') ?? 'not set';
    $dbDiagnostics['PGADMIN_PORT'] = $_ENV['PGADMIN_PORT'] ?? getenv('PGADMIN_PORT') ?? 'not set';
} else {
    $dbDiagnostics['MYSQL_PORT'] = $_ENV['MYSQL_PORT'] ?? getenv('MYSQL_PORT') ?? 'not set';
    $dbDiagnostics['PHPMYADMIN_PORT'] = $_ENV['PHPMYADMIN_PORT'] ?? getenv('PHPMYADMIN_PORT') ?? 'not set';
}
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title) ?></title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }

        .status {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }

        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem 0;
        }

        .info {
            background-color: #e2e3e5;
            border-color: #d6d8db;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }

        th,
        td {
            text-align: left;
            padding: 0.5rem;
            border-bottom: 1px solid #ddd;
        }
    </style>
</head>

<body>
    <h1><?= htmlspecialchars($title) ?></h1>

    <div class="card">
        <h2>Stack Overview</h2>
        <table>
            <tr>
                <th>Component</th>
                <th>Details</th>
                <th>Access</th>
            </tr>
            <tr>
                <td>Web Server</td>
                <td>Nginx + PHP-FPM</td>
                <td><a href="http://localhost:<?= htmlspecialchars($webPort) ?>" target="_blank">localhost:<?= htmlspecialchars($webPort) ?></a></td>
            </tr>
            <tr>
                <td>Database</td>
                <td><?= htmlspecialchars($dbTypeName) ?> <?= htmlspecialchars($_ENV['DB_DATABASE'] ?? 'test_project') ?></td>
                <td>localhost:<?= htmlspecialchars($dbPort) ?></td>
            </tr>
            <tr>
                <td>Database GUI</td>
                <td><?= htmlspecialchars($adminToolName) ?></td>
                <td><a href="http://localhost:<?= htmlspecialchars($adminPort) ?>" target="_blank">localhost:<?= htmlspecialchars($adminPort) ?></a></td>
            </tr>
        </table>
    </div>

    <div class="card info">
        <h2>Quick Links</h2>
        <ul>
            <li><a href="/info">PHP Info</a></li>
            <li><a href="http://localhost:<?= htmlspecialchars($adminPort) ?>" target="_blank"><?= htmlspecialchars($adminToolName) ?></a></li>
        </ul>
    </div>

    <div class="card">
        <h2>Database Connection Status</h2>
        <?php if ($connectionInfo['connected']): ?>
            <div class="status success">
                ✓ Connected to <?= htmlspecialchars($dbTypeName) ?> Server <?= htmlspecialchars($connectionInfo['server_version']) ?><br>
                Database: <?= htmlspecialchars($connectionInfo['database']) ?><br>
                User: <?= htmlspecialchars($connectionInfo['user']) ?><br>
                Host: <?= htmlspecialchars($connectionInfo['host'] ?? $dbHost) ?>
            </div>
        <?php else: ?>
            <div class="status error">
                ✗ Database connection failed: <?= htmlspecialchars($connectionInfo['error']) ?>
            </div>
            <div class="info">
                <h3>Connection Details</h3>
                <ul>
                    <?php foreach ($dbDiagnostics as $key => $value): ?>
                        <li><?= htmlspecialchars($key) ?>: <?= htmlspecialchars($value) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>
    </div>
</body>

</html>
