import importlib
import shutil
from pathlib import Path

import pytest

# Import TemplateManager lazily to avoid heavy dependencies during collection
TemplateManager = importlib.import_module(
    "chimera.core.template_manager").TemplateManager

STACK_MATRIX = [
    ("stacks/backend/php-web", "mysql"),
    ("stacks/backend/php-web", "mariadb"),
    ("stacks/backend/php-web", "postgresql"),
    ("stacks/fullstack/react-php", "mysql"),
]


@pytest.mark.parametrize("template_id,variant", STACK_MATRIX)
def test_cli_smoke(tmp_path: Path, template_id: str, variant: str):
    tm = TemplateManager(verbose=False)

    project_name = f"{Path(template_id).name}-{variant}"
    ok = tm.create_project(template_id, project_name,
                           target_dir=tmp_path, variant=variant)
    assert ok, f"create_project failed for {template_id}:{variant}"

    project_dir = tmp_path / project_name
    # Ensure canonical compose exists and no stray variant files remain
    assert project_dir.joinpath("docker-compose.yml").exists()
    stray = list(project_dir.glob("docker-compose.*.yml"))
    assert len(stray) == 0, f"Unexpected stray compose files found: {stray}"

    # Ensure .env generated
    assert project_dir.joinpath(".env").exists()

    # Cleanup to keep tmp dir small
    shutil.rmtree(project_dir)
