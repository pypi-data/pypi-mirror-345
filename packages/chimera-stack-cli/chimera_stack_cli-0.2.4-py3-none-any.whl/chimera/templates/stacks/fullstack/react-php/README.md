# React PHP Fullstack Stack

Welcome to your ChimeraStack-generated full-stack development environment! This stack gives you:

- React (TypeScript) frontend (served via Nginx at \`http://localhost:${WEB_PORT}\` with live dev-server on \`${FRONTEND_PORT}\`)
- PHP-FPM backend served through Nginx (reachable at http://localhost:${WEB_PORT})
- MySQL / MariaDB / PostgreSQL database with pre-seeded schema
- DB admin GUI (phpMyAdmin or pgAdmin) on http://localhost:${ADMIN_PORT}

---

## Getting started

```bash
# start containers in the background
$ docker-compose up -d

# tail logs (optional)
$ docker-compose logs -f --tail=50
```

After the containers are **healthy** you can visit:

| Service                     | URL                               |
| --------------------------- | --------------------------------- |
| Frontend (React SPA)        | http://localhost:${WEB_PORT}      |
| React Dev Server (optional) | http://localhost:${FRONTEND_PORT} |
| Backend API                 | http://localhost:${WEB_PORT}/api  |
| Database GUI                | http://localhost:${ADMIN_PORT}    |

---

## Development workflow

### Frontend

The frontend container runs `npm start` so it hot-reloads as you edit code.

```bash
# inside container (one-off)
$ docker compose exec frontend sh
/app $ npm install <package>
```

To run tests or other scripts, execute them in the container or add them to the package.json then restart.

### Backend

PHP files live under `backend/`. The web root is `backend/public/` and API routes are served from `backend/public/api`.

- Add new endpoints in `backend/public/api/`.
- Use `backend/bootstrap.php` for shared setup (autoloading, env, db).
- Live reload isn't required – Nginx + PHP-FPM auto-serve the updated files.

### Database

Connection details are injected via environment variables (see `docker-compose.*.yml`). Default creds:

```
DB_USER=${DB_USERNAME}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_DATABASE}
DB_HOST=db
```

Use the GUI or `docker compose exec db mysql -u$DB_USERNAME -p$DB_PASSWORD $DB_DATABASE`.

---

## Customising ports

The CLI auto-selects free ports at project creation. Edit `docker-compose*.yml` if you need to hard-code them; then recreate containers.

---

## Useful commands

```bash
# stop and remove containers
$ docker compose down

# rebuild images after Dockerfile changes
$ docker compose build --no-cache

# prune unused images/volumes
$ docker system prune
```

---

Happy hacking! 🎉
