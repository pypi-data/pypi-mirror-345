<?php

/**
 * Simple API for the React-PHP Fullstack Template
 *
 * This file provides endpoints to access user and post data.
 */

// Set headers for CORS and JSON response
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");
header("Content-Type: application/json");

// Include database setup
$dbSetup = require_once __DIR__ . '/../../database/init/setup-database.php';

// Extract the request path
$path = $_SERVER['PATH_INFO'] ?? '/';
$method = $_SERVER['REQUEST_METHOD'];

// Handle OPTIONS requests (CORS preflight)
if ($method === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Define routes
switch ($path) {
    case '/':
    case '':
        // API info
        echo json_encode([
            'name' => 'ChimeraStack API',
            'version' => '1.0.0',
            'endpoints' => [
                '/api/users' => 'Get all users',
                '/api/posts' => 'Get all posts'
            ]
        ]);
        break;

    case '/users':
        // Return sample users
        $users = [
            [
                'id' => 1,
                'name' => 'John Doe',
                'email' => 'john@example.com'
            ],
            [
                'id' => 2,
                'name' => 'Jane Smith',
                'email' => 'jane@example.com'
            ]
        ];

        echo json_encode($users);
        break;

    case '/posts':
        // Return sample posts
        $posts = [
            [
                'id' => 1,
                'user_id' => 1,
                'title' => 'Getting Started with React',
                'content' => 'React is a JavaScript library for building user interfaces...'
            ],
            [
                'id' => 2,
                'user_id' => 1,
                'title' => 'PHP 8.2 Features',
                'content' => 'PHP 8.2 brings several new features including...'
            ],
            [
                'id' => 3,
                'user_id' => 2,
                'title' => 'Docker Compose Basics',
                'content' => 'Docker Compose is a tool for defining multi-container applications...'
            ]
        ];

        echo json_encode($posts);
        break;

    default:
        // 404 Not Found
        http_response_code(404);
        echo json_encode(['error' => 'Not Found', 'message' => 'The requested endpoint does not exist']);
        break;
}
