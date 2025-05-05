# ChimeraStack Template Authoring Guide

> Build once, share with everyone. This document explains **how to create, test, and publish custom ChimeraStack templates** so that contributors can expand the catalogue with new languages, frameworks and services.

> **Moved from `docs/templates.md`** — this is now the canonical guide.

---

## 1. Mental Model

ChimeraStack templates are **lego bricks** that fall into two categories:

| Level     | Folder                         | Description                                                                                                        |
| --------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Core      | `templates/base/`              | Universal helpers (welcome page, shared configs, health-checks).                                                   |
| Component | `templates/base/<component>/`  | A reusable service unit (e.g. `mysql`, `redis`, `php`, `nginx`).                                                   |
| Stack     | `templates/stacks/<category>/` | A fully-fledged development stack composed of multiple components (e.g. `backend/php-web`, `fullstack/react-php`). |

When a user runs `chimera create my-app -t backend/php-web -v postgresql`, the CLI:

1. Collects the requested **stack** and its **component** dependencies.
2. Renders all files through the Jinja2 pipeline (variable substitution).
3. Allocates service ports (via `PortAllocator`).
4. Executes `post_copy` tasks for clean-up or additional provisioning.

---

## 2. Directory Layout

```text
templates/
│
├── base/
│   ├── core/                 # Shared assets (welcome page, scripts…)
│   ├── backend/
│   │   └── php/              # PHP-FPM component
│   └── database/
│       ├── mysql/
│       ├── postgresql/
│       └── mariadb/
│
└── stacks/
    └── backend/
        └── php-web/
            ├── compose/      # Optional compose fragments
            ├── template.yaml # Stack manifest (required)
            └── docker-compose.yml.j2  # Rendered to docker-compose.yml
```

**📝 Naming rule**: always use **kebab-case** IDs (`php-web`, `node-express`).

---

## 3. `template.yaml` Schema

Every template **MUST** ship a manifest. The JSON-Schema lives in `src/chimera/schema/template_schema.json`. Key fields:

| Field         | Type          | Required | Description                                    |
| ------------- | ------------- | -------- | ---------------------------------------------- |
| `name`        | string        | ✓        | Human-readable title shown in the CLI menu.    |
| `id`          | string        | ✓        | Kebab-case identifier (`backend/php-web`).     |
| `version`     | string        | ✓        | SemVer. Bump on breaking changes.              |
| `description` | string        | ✓        | Short explanation (~120 chars).                |
| `tags`        | array[string] | –        | Search keywords (`php`, `mysql`, `fullstack`). |
| `variables`   | object        | –        | Values exposed to Jinja2 (defaults & prompts). |
| `post_copy`   | array[object] | –        | Tasks executed after files are copied.         |

See the **example** under `templates/template.yaml.example`.

---

## 4. Compose & Jinja2 Rendering

1. **Compose fragments** — Large templates can be split into smaller files under `compose/` and imported with:

   ```yaml
   services:
     app:
       <<: *php
   ```

   The stack's main `docker-compose.yml.j2` can then `{% include 'compose/php.yml' %}`.

2. Use `{{ variable_name }}` placeholders anywhere in text files (Markdown, env, YAML…).
3. Global helpers are available:
   - `{{ ports.admin }}` – admin tool port
   - `{{ project_name }}` – directory name chosen by the user

> ℹ️ **CLI summary** – The `welcome_page` section drives the dynamic output shown after `chimera create` (Port Allocations, Next steps, Access URLs). Declare a section for each public-facing service so the ports are printed correctly.

---

## 5. `post_copy` Tasks

After rendering, ChimeraStack executes any declared "post-copy" tasks. Supported actions:

| Action    | Example                                      | Purpose                                                   |
| --------- | -------------------------------------------- | --------------------------------------------------------- |
| `delete`  | `delete: ["docker-compose.base.yml"]`        | Remove temp helper files.                                 |
| `rename`  | `rename: {from: ".env.example", to: ".env"}` | Finalise filenames.                                       |
| `command` | `command: "composer install --no-dev"`       | Run arbitrary shell command inside the generated project. |

Keep tasks **idempotent** to support re-creation.

---

## 6. Validation & Testing Workflow

1. **Local linting**

   ```bash
   pre-commit run --all-files  # schema validation & linting
   ```

2. **Unit tests** – add cases in `tests/templates/` to ensure ports & tasks behave.
3. **Integration smoke test**

   ```bash
   chimera create demo -t backend/php-web -v mysql
   cd demo && docker compose config
   ```

   The command must exit without errors.

CI will automatically run the validation script for every PR.

---

## 7. Best Practices

✔️ Keep **images lightweight** – pick runtime-only images, not full SDKs.

✔️ Provide `.env` files with sane defaults.

✔️ Expose **healthchecks** for each service (improves UX in `docker ps`).

✔️ Document any non-obvious decisions inside the template folder with `README.md`.

❌ **Avoid hard-coding ports** – always rely on `PortAllocator` ranges.

❌ **Do not commit secrets** – use environment variables / `.env` placeholders.

---

## 8. Publishing Your Template

1. Fork & clone the repo.
2. Create your template under `templates/…`.
3. Add tests & update `templates.yaml` catalogue if needed.
4. Commit with a semantic message: `feat(template): add django-postgres stack`.
5. Open a pull request – the GitHub Actions suite must pass before review.

Happy hacking! ✨

## 9. Declaring Database Variants

Templates can support multiple database engines through the **variants** feature:

```yaml
# Define available variants
variants:
  - mysql
  - postgresql
  - mariadb

# Stack-specific configuration
stack:
  type: "backend"
  default_database: "mysql" # Fallback when no variant specified
  supported_databases:
    - engine: "mysql"
      name: "MySQL"
      version: "8.0"
    - engine: "postgresql"
      name: "PostgreSQL"
      version: "15"
    - engine: "mariadb"
      name: "MariaDB"
      version: "11"
```

### Conditional Database Settings

Use Jinja2 conditionals in your `docker-compose.yml.j2` to select the appropriate settings:

```yaml
services:
  db:
    image: "{{ 'postgres:15-alpine' if DB_ENGINE == 'postgresql' else 'mariadb:11' if DB_ENGINE == 'mariadb' else 'mysql:8.0' }}"
    ports:
      - "${DB_PORT}:{{ '5432' if DB_ENGINE == 'postgresql' else '3306' }}"
```

### Conditional File Inclusion

You can conditionally include files based on the selected variant:

```yaml
files:
  - source: "docker/mysql/my.cnf"
    target: "docker/mysql/my.cnf"
    condition: "${DB_ENGINE} == 'mysql'"
```

### Cleanup Unused Variant Files

Use `post_copy` to remove files not needed for the selected variant:

```yaml
post_copy:
  - remove: "docker/mysql/my.cnf"
    condition: "${DB_ENGINE} != 'mysql'"
  - remove: "docker/mariadb/my.cnf"
    condition: "${DB_ENGINE} != 'mariadb'"
```

### Database Component Referencing

Reference the appropriate database component based on variant:

```yaml
components:
  database:
    source: "base/database/${DB_ENGINE}"
    required: true
```

This enables users to select a database variant with:

```python
TemplateManager().create_project(
    "stacks/backend/php-web",
    "myapi",
    variant="postgresql"  # or mysql, mariadb
)
```

## Full-stack Templates with Vite Frontend

When creating modern full-stack templates, using Vite for frontend development provides a much better developer experience than older bundlers. Here's how to structure a full-stack template with Vite:

### Frontend Configuration

1. **Vite + React Setup**:

   ```yaml
   post_create:
     - working_dir: "frontend"
       command: "npm create vite@latest . --template react-ts -- --skip-git"
     - working_dir: "frontend"
       command: "npm install"
   ```

2. **Adding Tailwind**:

   ```yaml
   post_create:
     # After Vite setup
     - working_dir: "frontend"
       command: "npm install -D tailwindcss postcss autoprefixer"
     - working_dir: "frontend"
       command: "npx tailwindcss init -p"
   ```

3. **Dockerfile for Vite** (dev + prod):
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build  # For production asset generation
   ENV FRONTEND_PORT=${FRONTEND_PORT}
   CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT}"]
   EXPOSE ${FRONTEND_PORT}
   ```

### Nginx Reverse Proxy

For full-stack templates, configure Nginx to route API requests to the backend while serving the frontend:

```nginx
# Serve static dashboard/welcome page
root /usr/share/nginx/html;

# API requests - proxy to backend
location /api/ {
    proxy_pass http://backend:80/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# Frontend - proxy to Vite dev server
location / {
    proxy_pass http://frontend:${FRONTEND_PORT};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

### Environment Variables

Use environment files to pass configuration from host to containers:

1. **Template .env**:

   ```
   VITE_API_URL=http://localhost:${WEB_PORT}/api
   ```

2. **Docker Compose Environment**:
   ```yaml
   frontend:
     environment:
       - "VITE_API_URL=http://localhost:${WEB_PORT}/api"
       - "FRONTEND_PORT=${FRONTEND_PORT}"
   ```

### Database Variants

For templates supporting multiple database types, use a Jinja2 template for `docker-compose.yml`:

```yaml
db:
  image: {{ "postgres:15-alpine" if DB_ENGINE=='postgresql'
            else "mariadb:11" if DB_ENGINE=='mariadb'
            else "mysql:8.0" }}
  ports:
    - "${DB_PORT}:{{ "5432" if DB_ENGINE=='postgresql' else "3306" }}"
  environment:
    {% if DB_ENGINE == 'postgresql' %}
    - "POSTGRES_DB=${DB_DATABASE}"
    {% else %}
    - "MYSQL_DATABASE=${DB_DATABASE}"
    {% endif %}
```

This pattern makes it easy to maintain a single `docker-compose.yml.j2` file that supports all database variants.

## Frontend-Only Templates with Vite

For single-service frontend applications that don't require a backend or database, you can create lightweight templates that use Vite for development and Nginx for serving:

### Template Configuration

```yaml
name: "React Static"
description: "Vite + React + Tailwind single-service stack"
type: "stack"
version: "1.0.0"
tags:
  - frontend
  - react
  - vite

stack:
  default_database: none # Skip database logic
  frontend:
    framework: "react"
    version: "18"
    dev_server: true

variants: ["default"] # Only one variant needed

components:
  core_welcome:
    source: "base/core/welcome"
    required: true
```

### Nginx Configuration

For frontend-only templates, the Nginx configuration is simpler as it only needs to proxy requests to the Vite dev server:

```nginx
server {
    listen 80;

    # Serve welcome dashboard from standard location
    root /usr/share/nginx/html;

    # All requests - proxy to frontend
    location / {
        proxy_pass http://frontend:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Docker Setup for Frontend Templates

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Build for production (assets in /app/dist)
RUN npm run build
# Development mode
ARG FRONTEND_PORT=3000
ENV FRONTEND_PORT=${FRONTEND_PORT}
CMD ["npm","run","dev","--","--host","0.0.0.0","--port","${FRONTEND_PORT}"]
```

This setup allows for both development mode with HMR and builds production-ready assets.

### Environment Variables

Only minimal environment variables are needed:

```
FRONTEND_PORT=${FRONTEND_PORT}
VITE_BACKEND_URL=http://localhost:${WEB_PORT}/api  # For future integrations
```

The `VITE_` prefix is required for variables to be exposed to the frontend in Vite.
