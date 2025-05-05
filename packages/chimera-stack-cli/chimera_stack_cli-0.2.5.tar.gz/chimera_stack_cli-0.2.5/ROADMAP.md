# 🛣️ ChimeraStack CLI Roadmap

_Last updated: **4 May 2025** &nbsp;•&nbsp; HEAD `v0.2.5.dev17` (main)_

> Milestones = outcome‑level; sprint tickets live in [`TODO.md`](TODO.md).

---

## ✅ 0.2.0 — Template Refactor (Shipped 26 Mar 2025)

- `base/` + `stacks/` taxonomy
- Dynamic Port Allocator
- Jinja2 rendering + YAML schema validation
- Initial unit‑test pyramid

## ✅ 0.2.1 → 0.2.4 — Packaging & Pipeline

- Pure `pyproject.toml` + **setuptools‑scm**
- Wheel + sdist + PyInstaller binaries
- GHCR Docker image
- Git history cleaned
- Unit → snapshot → smoke CI scaffolded

---

## 🚧 0.2.5 — **Sentinel Template Pack I + Core Dashboard**  (_current work_)

| Area                            | Deliverable                                                                                                                                                                                                                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Universal proxy + dashboard** | `nginx‑proxy` container ships in **every** stack.<br>`base/core/welcome/` component provides `welcome.html.j2` (Tailwind) served by proxy.                                                                                                                                          |
| **Sentinel templates**          | • `backend/php-web` — PHP‑FPM + proxy + MySQL (✓), **add PostgreSQL & MariaDB**; phpMyAdmin/pgAdmin links.<br>• `fullstack/react-php` — React (Vite + Tailwind) + refreshed backend + proxy.<br>• **new** `frontend/react-static` — React (Vite + Tailwind) served solely by proxy. |
| **Port‑range cleanup**          | All ranges moved to `config/ports.yaml`; allocator removed hard‑coded fallback.                                                                                                                                                                                                     |
| **Testing**                     | Snapshot + smoke for every template/variant; unit check for zero `{{…}}` placeholders.                                                                                                                                                                                              |
| **Manual matrix QA**            | Run by maintainer after CI green.                                                                                                                                                                                                                                                   |
| **Release**                     | Tag **v0.2.5** when automated + manual checks pass.                                                                                                                                                                                                                                 |

---

## 🛠️ 0.2.6 — **ServiceGraph Core Refactor**

- Introduce `ServiceGraph` (nodes: `proxy`, `dashboard`, `frontend`, `backend`, `database`, `admin`, `extra`)
- TemplateManager → build graph → render compose/env
- Dashboard node re‑renders links after graph mutation
- Legacy monolithic cleanup removed; declarative `post_copy` only
- `ruff` + `mypy` added; core modules typed

---

## 🔌 0.2.7 — **Plugin System MVP**

- `chimera.plugins` entry‑point discovery
- Sample plugins: `chimera add redis`, `chimera add netdata`
- Plugin mutates graph; port collision detection; dashboard updates

---

## 📦 0.3.0 — **Template Expansion A**

- `fullstack/django-react-postgres` (includes Adminer)
- Community template submission workflow & CI validator

---

## 🔀 0.3.1 — **Mix‑&‑Match Init**

`chimera init --frontend react --backend node --db postgres --extras redis,netdata`

- Full graph builder + diff engine
- Auto port/env stitching & dashboard generation

---

## ☁️ 0.3.2 — **Deploy Command**

- `chimera deploy` → Coolify & generic SSH targets
- Let’s Encrypt helper; zero‑downtime DB import
- Generate `docker-compose.prod.yml` (no bind mounts, prod env flags)

---

## 🗓️ Version ↔ Milestone Matrix

| Version | Milestone                           |
| ------- | ----------------------------------- |
| 0.2.0   | Template Refactor                   |
| 0.2.4   | Packaging & Pipeline                |
| 0.2.5   | Sentinel Templates + Core Dashboard |
| 0.2.6   | ServiceGraph Core                   |
| 0.2.7   | Plugin System MVP                   |
| 0.3.0   | Template Expansion A                |
| 0.3.1   | Mix‑&‑Match Init                    |
| 0.3.2   | Deploy Command                      |

---

## 🔮 Backlog / Nice‑to‑Have

- Port lockfile persistence (`~/.chimera/ports.json`)
- `chimera update` command to bump existing projects
- VS Code `devcontainer.json` generator
- `chimera doctor` diagnostic command
