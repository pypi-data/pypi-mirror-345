import tempfile
from pathlib import Path
import yaml


from chimera.core.template_manager import TemplateManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _render_stack(tmp_dir: Path, variant: str) -> Path:
    """Generate the full-stack React-PHP template with the given *variant*.

    Returns
    -------
    Path
        Path to the generated project directory.
    """

    tm = TemplateManager(verbose=False)
    project_name = f"fs-{variant}"
    ok = tm.create_project(
        template_id="stacks/fullstack/react-php",
        project_name=project_name,
        variant=variant,
        target_dir=tmp_dir,
    )

    assert ok, "Project generation failed"
    return tmp_dir / project_name


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _assert_compose_consistency(compose_path: Path):
    """Ensure every *depends_on* value refers to an existing service."""

    content = yaml.safe_load(compose_path.read_text())

    services = content.get("services", {})
    declared = set(services.keys())

    for svc_name, svc_def in services.items():
        depends_on = []
        if isinstance(svc_def, dict) and "depends_on" in svc_def:
            raw = svc_def["depends_on"]
            if isinstance(raw, list):
                depends_on = raw
            elif isinstance(raw, dict):
                depends_on = list(raw.keys())

        for dep in depends_on:
            assert (
                dep in declared
            ), f"Service '{svc_name}' depends on undefined service '{dep}'"


# Parametrise for database variants


def test_fullstack_compose_dependencies(tmp_path: Path):
    """docker-compose.yml must be internally consistent for each variant."""

    for variant in ("mysql", "mariadb", "postgresql"):
        project_dir = _render_stack(tmp_path, variant)
        compose_path = project_dir / "docker-compose.yml"

        assert compose_path.exists(), "docker-compose.yml not found"

        _assert_compose_consistency(compose_path)
