<?php

declare(strict_types=1);

class Database
{
    private static $instance = null;
    private $pdo;
    private $connected = false;
    private $error = null;

    private function __construct()
    {
        try {
            // Try to get environment variables from both $_ENV and getenv()
            $host = $_ENV['DB_HOST'] ?? getenv('DB_HOST') ?? 'mysql';
            $database = $_ENV['DB_DATABASE'] ?? getenv('DB_DATABASE') ?? 'chimera';
            $username = $_ENV['DB_USERNAME'] ?? getenv('DB_USERNAME') ?? 'chimera';
            $password = $_ENV['DB_PASSWORD'] ?? getenv('DB_PASSWORD') ?? 'secret';
            $port = $_ENV['DB_PORT'] ?? getenv('DB_PORT') ?? '3306';
            $engine = $_ENV['DB_ENGINE'] ?? getenv('DB_ENGINE') ?? 'mysql';

            // Build proper DSN based on database engine
            if ($engine === 'postgresql') {
                $dsn = "pgsql:host={$host};port={$port};dbname={$database}";
            } else {
                // Both MySQL and MariaDB use the same PDO driver
                $dsn = "mysql:host={$host};port={$port};dbname={$database}";
            }

            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ];

            $this->pdo = new PDO($dsn, $username, $password, $options);
            $this->connected = true;
        } catch (PDOException $e) {
            $this->error = $e->getMessage();
        }
    }

    public static function getInstance()
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function getPdo()
    {
        return $this->pdo;
    }

    public function isConnected()
    {
        return $this->connected;
    }

    public function getError()
    {
        return $this->error;
    }

    public function getConnectionInfo()
    {
        if ($this->isConnected()) {
            $engine = $_ENV['DB_ENGINE'] ?? getenv('DB_ENGINE') ?? 'mysql';
            $host = $_ENV['DB_HOST'] ?? getenv('DB_HOST') ?? 'mysql';
            $database = $_ENV['DB_DATABASE'] ?? getenv('DB_DATABASE') ?? 'chimera';
            $username = $_ENV['DB_USERNAME'] ?? getenv('DB_USERNAME') ?? 'chimera';

            if ($engine === 'postgresql') {
                $version = $this->pdo->query('SELECT version()')->fetchColumn();
            } else {
                $version = $this->pdo->query('SELECT version()')->fetchColumn();
            }

            return [
                'connected' => true,
                'database_type' => $engine,
                'server_version' => $version,
                'database' => $database,
                'user' => $username,
                'host' => $host
            ];
        }

        return [
            'connected' => false,
            'error' => $this->error
        ];
    }
}
