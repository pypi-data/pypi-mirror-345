# 📝 ChimeraStack CLI Sprint Board

_Updated May 3 2025_

Keep it lightweight: tick a box, push, repeat.

---

## 🟢 Sprint 1 — Packaging & CI Cleanup (🎯 v0.2.4)

### 1 · Packaging

- [x] Remove `setup.py` & `setup.cfg`
- [x] Adopt **setuptools‑scm** (`dynamic = ["version"]` in *pyproject.toml*)
- [x] Expose `__version__` in `src/chimera/__init__.py`

### 2 · CI / Release Pipeline

- [x] Switch to `pipx run build`
- [x] Upload wheel + sdist to PyPI on tag
- [x] Build & push Docker image `ghcr.io/chimera/cli:<tag>`
- [x] Build PyInstaller bundles (macOS & Linux) → attach to GitHub Release

### 3 · Repo Hygiene

- [x] Purge historical binaries with _git filter‑repo_
- [x] Add `releases/` & `dist/` to `.gitignore`

---

## 🟡 Sprint 2 — ComposeGraph Refactor + Sentinel Templates (🎯 v0.2.5)

### 4.1 · Unit Tests (first)

- [ ] Add pytest fixture that patches `docker.from_env`
- [ ] Write edge‑case tests for `PortAllocator.allocate()`

### 4.2 · Core Graph

- [ ] Implement `compose_graph.py`
- [ ] Integrate `PortAllocator.allocate()` into graph nodes
- [ ] Refactor `TemplateManager` to build → validate → render graph

### 4.3 · Sentinel Templates

- [ ] **frontend/react-static** – add Chimera welcome elements
- [ ] **backend/php-web** – Nginx + 3 DB variants; welcome page links
- [ ] **fullstack/react-php** – verify against new graph, fix drift

### 4.4 · Snapshot & Smoke Tests

- [ ] Snapshot: rendered compose YAML for `react-static`
- [ ] Smoke: `chimera create … && docker compose config` on all sentinel stacks

### 4.5 · Project Stamp

- [ ] Write `.chimera.yml` (`cli_version`, `created_at`) to generated projects

### 4.6 · Docs

- [ ] Update README & authoring docs for new graph flow
- [ ] CONTRIBUTING: how to run tests without Docker

---

## 🟠 Sprint 3 — Plugin MVP (🎯 v0.3.0)

### 9 · Plugin API

- [ ] Define `chimera.plugin_api` base class
- [ ] Entry‑point discovery (`[chimera.plugins]` in *pyproject.toml*)
- [ ] Typer auto‑mount: `chimera add <plugin>`

### 10 · Sample Plugins

- [ ] **Redis** (single service)
- [ ] **Netdata** (monitoring stack)

### 11 · Validation

- [ ] Conflict & port‑collision checker after plugin mutations
- [ ] Snapshot tests for plugin‑augmented compose output

---

## 🟣 Sprint 4 — Template Expansion A (🎯 v0.3.1)

- [ ] `fullstack/django-react-postgres`
- [ ] Document community submission workflow
- [ ] Integrate first community template (stretch)

---

## 🔮 Backlog / Nice‑to‑Have

- [ ] Port lockfile persistence (`~/.chimera/ports.json`)
- [ ] `chimera update` to bump an existing project’s stack
- [ ] VS Code devcontainer generator
