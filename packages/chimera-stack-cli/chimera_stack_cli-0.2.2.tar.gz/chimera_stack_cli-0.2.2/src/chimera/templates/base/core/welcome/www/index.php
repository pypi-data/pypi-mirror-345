<?php
declare(strict_types=1);

require_once __DIR__ . '/../src/bootstrap.php';

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

switch ($uri) {
    case '/':
        require __DIR__ . '/../src/pages/home.php';
        break;
    case '/info':
        phpinfo();
        break;
    case '/health':
        header('Content-Type: text/plain');
        echo 'healthy';
        break;
    default:
        http_response_code(404);
        echo "404 Not Found";
        break;
}
