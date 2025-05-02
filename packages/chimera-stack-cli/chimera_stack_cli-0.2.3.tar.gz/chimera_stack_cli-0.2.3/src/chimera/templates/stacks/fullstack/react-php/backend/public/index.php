<?php

/**
 * Main entry point for the PHP backend
 */

// Check if this is an API request
if (strpos($_SERVER['REQUEST_URI'], '/api') === 0) {
    // Include the API router
    include __DIR__ . '/api/index.php';
    exit;
}

// For non-API requests, show a welcome page
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChimeraStack PHP Backend</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            background-color: #4CAF50;
            color: white;
            text-align: center;
            padding: 2rem;
        }

        main {
            flex: 1;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        footer {
            background-color: #f5f5f5;
            text-align: center;
            padding: 1rem;
            margin-top: auto;
        }

        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }

        .endpoint {
            background-color: #f9f9f9;
            border-left: 4px solid #4CAF50;
            padding: 1rem;
        }

        code {
            background-color: #f5f5f5;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
        }

        .btn {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin-top: 1rem;
        }
    </style>
</head>

<body>
    <header>
        <h1>ChimeraStack PHP Backend</h1>
        <p>Your API server is up and running</p>
    </header>

    <main>
        <div class="card">
            <h2>🚀 API Information</h2>
            <p>This is the backend API for your ChimeraStack fullstack application. Your React frontend can connect to this API to fetch and manipulate data.</p>

            <h3>Available Endpoints:</h3>
            <div class="endpoints">
                <div class="endpoint">
                    <h4>API Base</h4>
                    <code>GET /api</code>
                    <p>Returns information about the API</p>
                    <a href="/api" class="btn">Try it</a>
                </div>

                <div class="endpoint">
                    <h4>Users</h4>
                    <code>GET /api/users</code>
                    <p>Returns a list of users</p>
                    <a href="/api/users" class="btn">Try it</a>
                </div>

                <div class="endpoint">
                    <h4>Posts</h4>
                    <code>GET /api/posts</code>
                    <p>Returns a list of posts</p>
                    <a href="/api/posts" class="btn">Try it</a>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔄 Frontend Connection</h2>
            <p>Your React frontend should be configured to connect to this API. Make sure the environment variable <code>REACT_APP_API_URL</code> is set correctly in your frontend's <code>.env</code> file.</p>
            <p>Default API URL: <code>http://localhost:<?php echo getenv('WEB_PORT') ?: '8000'; ?>/api</code></p>
        </div>

        <div class="card">
            <h2>📊 Database Connection</h2>
            <p>Database configuration:</p>
            <ul>
                <li>Type: <code><?php echo getenv('DB_CONNECTION') ?: 'mysql'; ?></code></li>
                <li>Host: <code><?php echo getenv('DB_HOST') ?: 'db'; ?></code></li>
                <li>Port: <code><?php echo getenv('DB_PORT') ?: '3306'; ?></code></li>
                <li>Database: <code><?php echo getenv('DB_DATABASE') ?: 'database'; ?></code></li>
                <li>Username: <code><?php echo getenv('DB_USERNAME') ?: 'username'; ?></code></li>
            </ul>
        </div>
    </main>

    <footer>
        <p>Powered by ChimeraStack | PHP Backend</p>
    </footer>
</body>

</html>
