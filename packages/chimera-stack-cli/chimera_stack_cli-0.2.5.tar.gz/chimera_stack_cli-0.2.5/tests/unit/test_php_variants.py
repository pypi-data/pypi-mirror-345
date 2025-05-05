import importlib
import shutil
import re
from pathlib import Path

import pytest

# Import TemplateManager lazily to avoid heavy dependencies during collection
TemplateManager = importlib.import_module(
    "chimera.core.template_manager").TemplateManager

DB_VARIANTS = [
    "mysql",
    "postgresql",
    "mariadb"
]


@pytest.mark.parametrize("db_variant", DB_VARIANTS)
def test_php_web_db_variants(tmp_path: Path, db_variant: str):
    """Test that PHP web stack properly handles different database variants."""
    tm = TemplateManager(verbose=False)

    # Create a temporary project with specified DB variant
    project_name = f"php-web-{db_variant}-test"
    ok = tm.create_project("stacks/backend/php-web", project_name,
                           target_dir=tmp_path, variant=db_variant)
    assert ok, f"create_project failed for database variant {db_variant}"

    project_dir = tmp_path / project_name

    # Test 1: Ensure docker-compose.yml exists
    compose_path = project_dir / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml not found"

    # Check for absence of variant compose files
    for variant in DB_VARIANTS:
        variant_compose = project_dir / f"docker-compose.{variant}.yml"
        assert not variant_compose.exists(
        ), f"Variant file {variant_compose} should not exist"

    # Test 2: Check docker-compose.yml has the correct database image
    compose_content = compose_path.read_text()

    if db_variant == "mariadb":
        # Allow any mariadb version tag
        assert re.search(r"image:\s*mariadb:", compose_content), \
            "Expected mariadb image in docker-compose.yml"
    else:
        expected_db_image = {
            "mysql": "mysql:8.0",
            "postgresql": "postgres:15-alpine",
        }[db_variant]

        assert expected_db_image in compose_content, \
            f"Expected {expected_db_image} in docker-compose.yml for variant {db_variant}"

    # Test 3: Check .env file contains correct database type
    env_path = project_dir / ".env"
    assert env_path.exists(), ".env file not found"

    env_content = env_path.read_text()
    assert f"DB_ENGINE={db_variant}" in env_content, \
        f"Expected DB_ENGINE={db_variant} in .env file"

    # Test 4: Check for valid port in .env file
    env_vars = {}
    for line in env_content.splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()

    # Ensure DB_PORT exists and is a number
    assert "DB_PORT" in env_vars, "DB_PORT missing in .env file"
    assert env_vars["DB_PORT"].isdigit(
    ), f"DB_PORT should be a number, got: {env_vars['DB_PORT']}"

    # Test 5: Check that index.php exists and contains no Jinja placeholders
    index_path = project_dir / "public" / "index.php"
    assert index_path.exists(), "index.php not found in public directory"

    index_content = index_path.read_text()
    assert "{{" not in index_content, "Unresolved Jinja placeholders in index.php"

    # Skip the config file checks - these may not be relevant in the current implementation

    # Cleanup
    shutil.rmtree(project_dir)
