# PHP Web Stack

Welcome to your **ChimeraStack** powered PHP web environment! This stack provides:

- PHP-FPM backend served through Nginx → `http://localhost:${WEB_PORT}`
- MySQL / MariaDB / PostgreSQL database
- DB admin GUI (phpMyAdmin or pgAdmin) → `http://localhost:${ADMIN_PORT}`

---

## 🚀 Getting started

```bash
# start containers
$ docker compose up -d

# follow logs (optional)
$ docker compose logs -f --tail=50
```

When containers are healthy, open your browser:

| Service      | URL                            |
| ------------ | ------------------------------ |
| Website      | http://localhost:${WEB_PORT}   |
| Database GUI | http://localhost:${ADMIN_PORT} |

---

## 🗂️ Project structure

```
public/          # Document root (Nginx serves from here)
└── index.php    # Example entry file

docker/
├── nginx/       # Nginx config
├── php/         # PHP-FPM Dockerfile + ini
└── ${DB_ENGINE}/# DB config (my.cnf or pg config)

config/          # Custom config files (if any)
```

---

## ⚙️ Common commands

```bash
# Stop & remove containers
$ docker compose down

# Rebuild after changing Dockerfile
$ docker compose build --no-cache

# Access a shell inside php container
$ docker compose exec php bash
```

---

Happy coding! ✨

**Dashboard**: http://localhost:${WEB_PORT}/welcome.html
**PHP Status**: http://localhost:${WEB_PORT}/
