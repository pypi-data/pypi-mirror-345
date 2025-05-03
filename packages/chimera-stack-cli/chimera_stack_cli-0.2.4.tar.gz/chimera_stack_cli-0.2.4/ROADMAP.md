# 🛣️ ChimeraStack CLI Roadmap

_Updated May 3 2025_

> Milestones only. Day‑to‑day tasks live in [`TODO.md`](TODO.md).

---

## ✅ v0.2.0 — Template Refactor _(shipped 26 Mar 2025)_

- New template categories (`base`, `stacks`)
- Dynamic port allocator
- Jinja2 renderer + validation
- Initial tests

## ✅ v0.2.1 – v0.2.3 — Hot‑fix Train

- Dependency pinning, URL fixes, minor CLI polish

---

## 🚧 v0.2.4 — Packaging & Release Pipeline _(current sprint)_

| Goal                           | Detail                                              |
| ------------------------------ | --------------------------------------------------- |
| Pure‑`pyproject` build         | Drop `setup.py`; adopt **setuptools‑scm**           |
| Single source of version truth | Git tag → `__version__`                             |
| Repo hygiene                   | Strip historical binaries; `.gitignore` `releases/` |
| Official Docker image          | `ghcr.io/chimera/cli:<tag>`                         |
| Test‑pyramid foundation        | Unit (mocked Docker) ➜ Snapshot ➜ Smoke             |

---

## 🔨 v0.2.5 — ComposeGraph Core + Sentinel Templates

- **ComposeGraph** internal model
- Refactor `TemplateManager` ➜ graph ➜ renderer
- Integrate `PortAllocator` into graph
- **Sentinel template trio**
  - `frontend/react-static` – single‑service, edited React welcome page
  - `backend/php-web` – PHP + Nginx + **mysql / postgresql / mariadb** variants, Chimerastack welcome page with port links
  - `fullstack/react-php` – existing stack retained as regression test

---

## 🔌 v0.3.0 — Plugin System MVP

- Entry‑point discovery (`chimera.plugins`)
- `chimera add <plugin>` Typer sub‑command
- Sample plugins: **Redis**, **Netdata**
- Port‑collision detection after plugin mutations

---

## 📦 v0.3.1 — Template Expansion A

- `fullstack/django-react-postgres`
- Community template submission process

---

## 🔀 v0.4.0 — Mix‑&‑Match Init

`chimera init --frontend react --backend node --db postgres`

---

## ☁️ v0.5.0 — Deployments

`chimera deploy` to Coolify or generic SSH target with Let’s Encrypt helper

---

### Version ↔ Milestone

| Version | Milestone                              |
| ------- | -------------------------------------- |
| 0.2.0   | Template refactor                      |
| 0.2.4   | Packaging & pipeline cleanup           |
| 0.2.5   | ComposeGraph core + sentinel templates |
| 0.3.0   | Plugin system MVP                      |
| 0.3.1   | Template expansion A                   |
| 0.4.0   | Mix‑&‑Match init                       |
| 0.5.0   | Deployments                            |
