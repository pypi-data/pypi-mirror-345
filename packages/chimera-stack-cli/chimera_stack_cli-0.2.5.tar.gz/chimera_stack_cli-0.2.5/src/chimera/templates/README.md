# ChimeraStack CLI Templates

This directory contains templates for ChimeraStack CLI. Templates are organized into a hierarchical structure:

- `base/` - Base components that can be composed into stacks
  - `backend/` - Backend components (PHP, Node.js, etc.)
  - `database/` - Database components (MySQL, PostgreSQL, MariaDB)
  - `frontend/` - Frontend components (React, Vue, etc.)
- `stacks/` - Complete application stacks
  - `frontend/` - Frontend-only stacks
  - `backend/` - Backend stacks with database
  - `fullstack/` - Full-stack applications

## Sentinel Templates

The following sentinel templates are available:

### 1. `stacks/frontend/react-static`

A static React application with a development server.

```bash
chimera create my-react-app -t frontend/react-static
```

### 2. `stacks/backend/php-web`

A PHP web application with Nginx and a database (MySQL, PostgreSQL, or MariaDB).

```bash
# Default (MySQL)
chimera create my-php-app -t backend/php-web

# With PostgreSQL
chimera create my-php-app -t backend/php-web -v postgresql

# With MariaDB
chimera create my-php-app -t backend/php-web -v mariadb
```

### 3. `stacks/fullstack/react-php`

A full-stack application with React frontend, PHP backend, and a database.

```bash
# Default (MySQL)
chimera create my-fullstack-app -t fullstack/react-php

# With PostgreSQL
chimera create my-fullstack-app -t fullstack/react-php -v postgresql

# With MariaDB
chimera create my-fullstack-app -t fullstack/react-php -v mariadb
```

## Dynamic Variables

The templates use Jinja2 templating for dynamic content generation. The following variables are available:

- `project_name` - Name of the project
- `ports` - Dictionary of allocated ports
  - `ports.web` - Web server port
  - `ports.frontend` - Frontend development server port
  - `ports.db` - Database port
  - `ports.admin` - Admin tool port (phpMyAdmin or pgAdmin)
- `services` - Dictionary of service information
- `db_variant` - Database variant (mysql, postgresql, mariadb)
- `cli_version` - ChimeraStack CLI version

## Creating Custom Templates

To create a custom template:

1. Create a directory in the appropriate category (frontend, backend, fullstack)
2. Create a `template.yaml` file with the template configuration
3. Create Docker Compose files and assets
4. Add post-copy tasks for rendering dynamic content

See the [Template Authoring Guide](../docs/authoring-templates.md) for details.
