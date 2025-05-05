# 📝 ChimeraStack CLI Sprint Board

_Last updated: 4 May 2025_

Lightweight rule: **tick a box, push, repeat**.

---

## 🟢 Sprint 1 — Packaging & CI Cleanup (✅ shipped in v0.2.4)

### 1 · Packaging

- [x] Remove `setup.py` & `setup.cfg`
- [x] Adopt **setuptools‑scm** (`dynamic = ["version"]`)
- [x] Expose `__version__` in `chimera.__init__`

### 2 · CI / Release Pipeline

- [x] Switch to `pipx run build`
- [x] Wheel + sdist upload to PyPI on tag
- [x] Build & push Docker image `ghcr.io/chimera/cli:<tag>`
- [x] Build PyInstaller bundles (macOS & Linux) → attach to release

### 3 · Repo Hygiene

- [x] Purge historical binaries (`git filter‑repo`)
- [x] Add `releases/`, `dist/` to `.gitignore`

---

## 🟡 Sprint 2 — Sentinel Templates + Core Dashboard (🎯 v0.2.5)

### 1 · Core Dashboard

- [x] **Create component** `base/core/welcome/`
  - [x] `nginx/conf.d/default.conf` (root → `/usr/share/nginx/html`)
  - [x] `www/welcome.html.j2` (Tailwind, dynamic links)
  - [x] `template.yaml` with `post_copy` to inject into every stack
- [x] Inject component into all stacks via `TemplateManager`
- [x] Unit test: generated projects contain `welcome.html` with no unresolved `{{ … }}`

### 2 · Template Authoring

- **backend/php-web**
  - [x] Migrate MySQL variant to declarative `post_copy` only
  - [x] Add PostgreSQL variant
  - [x] Add MariaDB variant
  - [x] Embed port‑link cards on PHP welcome page
- **fullstack/react-php**
  - [x] Update frontend to Vite + Tailwind
  - [x] Point proxy to `/api` for backend
  - [x] Ensure DB variants map correctly
- **frontend/react-static**
  - [x] Author Vite + Tailwind template folder
  - [x] Dockerfile + `.dockerignore`
  - [x] Make proxy serve built assets
  - [x] All stacks/variants build successfully; dashboard & links verified

### 3 · Port Allocator Cleanup

- [ ] Move remaining hard‑coded ranges to `config/ports.yaml`
- [ ] Add admin‑tool ranges `8081‑8099`
- [ ] Validation: allocator errors if YAML missing expected service

### 4 · Automated Tests & CI

- [ ] Snapshot test (`docker-compose.yml`, `.env`) for every template/variant
- [ ] Smoke test: `chimera create … && docker compose config` (GitHub Actions)
- [ ] Unit test: assert zero `{{ … }}` tokens post‑render

### 5 · Docs & DX

- [x] Update root `README.md` quick‑start (proxy + dashboard)
- [x] Author "Add your own template in 5 steps" in `docs/authoring-templates.md`

### 6 · Manual Matrix QA — _maintainer-only_ (✅ complete)

- [x] `chimera --version` shows semver tag
- [x] `chimera list` displays all sentinel templates with variants
- [x] Generate every template/variant (`chimera create test-<id>`)
- [x] Verify dashboard links, `.env`, port allocations
- [x] `docker compose up --build` → all containers **healthy**
- [x] Filed issues for any regressions (none found)

### 7 · Release

- [ ] Tag **v0.2.5‑rc1** → pipeline green
- [ ] Tag **v0.2.5** after manual QA passes

---

## 🟠 Sprint 3 — ServiceGraph Core (🎯 v0.2.6)

### 1 · Graph Layer

- [ ] Implement `ServiceGraph`, `ServiceNode`, `Edge`
- [ ] TemplateManager builds graph → renders compose/env
- [ ] Dashboard node re‑renders links from graph

### 2 · Cleanup Migration

- [ ] Convert remaining stacks/components to declarative `post_copy`
- [ ] Delete `_cleanup_project_structure` and its tests

### 3 · Allocator Enhancements

- [ ] Release ports on CLI exit (cache eviction)
- [ ] Support YAML comments/aliases in `config/ports.yaml`

### 4 · Static Analysis

- [ ] Add `ruff` and `mypy` to pre‑commit + CI
- [ ] Type‑annotate `template_manager`, `port_*`, `render`

### 5 · Cross‑Platform Smoke

- [ ] Windows & macOS runners (GitHub Actions) with Docker context workaround
- [ ] Mark flaky tests and open issues

### 6 · Docs & Release

- [ ] Update dev guide: ServiceGraph API, component spec
- [ ] Tag **v0.2.6‑rc1** → publish when CI green

---

## 🟣 Sprint 4 — Plugin System MVP (🎯 v0.2.7)

### 1 · Plugin API

- [ ] Design `chimera.plugin_api` base class
- [ ] `[chimera.plugins]` entry‑point discovery
- [ ] CLI sub‑command `chimera add <plugin>`

### 2 · Sample Plugins

- [ ] `redis` – single service
- [ ] `netdata` – monitoring stack

### 3 · Collision Handling

- [ ] Detect port clashes after graph mutation
- [ ] Re‑render dashboard with new links

### 4 · Tests & Docs

- [ ] Snapshot tests for plugin‑augmented compose output
- [ ] Update docs: how to write a plugin
- [ ] Tag **v0.2.7**

---

## 🔮 Backlog / Nice‑to‑Have

- [ ] Port lockfile persistence (`~/.chimera/ports.json`)
- [ ] `chimera update` command to bump existing projects
- [ ] VS Code `devcontainer.json` generator
- [ ] `chimera doctor` diagnostic command
- [ ] Prod compose generator (`docker-compose.prod.yml`)
