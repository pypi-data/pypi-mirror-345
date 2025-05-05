<?php

/**
 * ChimeraStack PHP Welcome Page
 * Generated for {{ project_name }}
 */
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }} - ChimeraStack</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.5;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }

        .card {
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .header {
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
        }

        .header h1 {
            margin-left: 1rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th,
        td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #f9f9f9;
        }
    </style>
</head>

<body>
    <div class="header">
        <h1>{{ project_name }}</h1>
    </div>

    <div class="card">
        <h2>🚀 Your PHP Project is Running!</h2>
        <p>This is a PHP project created with ChimeraStack CLI. You can start editing the files in the <code>public</code> directory.</p>
    </div>

    <div class="card">
        <h2>📋 Available Services</h2>
        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th>URL</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>PHP Application</td>
                    <td><a href="http://localhost:{{ ports.web }}" target="_blank">http://localhost:{{ ports.web }}</a></td>
                </tr>
                <tr>
                    <td>Database Admin</td>
                    <td><a href="http://localhost:{{ ports.admin }}" target="_blank">http://localhost:{{ ports.admin }}</a></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>💾 Database Information</h2>
        <ul>
            <li><strong>Type:</strong> {{ db_variant }}</li>
            <li><strong>Host:</strong> {{ db_variant }}</li>
            <li><strong>Port:</strong> {{ ports.db }}</li>
            <li><strong>Database:</strong> {{ project_name }}</li>
            <li><strong>Username:</strong> {{ project_name }}</li>
            <li><strong>Password:</strong> secret</li>
        </ul>
    </div>
</body>

</html>
