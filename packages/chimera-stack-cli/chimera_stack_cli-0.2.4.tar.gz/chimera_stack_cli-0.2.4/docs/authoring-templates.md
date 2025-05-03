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
