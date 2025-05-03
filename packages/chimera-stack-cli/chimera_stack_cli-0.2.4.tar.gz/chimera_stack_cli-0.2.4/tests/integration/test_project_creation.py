import pytest
import subprocess
import shutil
from pathlib import Path
from chimera.core import TemplateManager
import os


@pytest.mark.integration
def test_project_creation_and_compose_validation(tmp_path):
    """
    Integration test that:
    1. Creates a project using the CLI
    2. Validates the docker-compose configuration
    3. Checks that all required files are present
    4. Verifies the project structure
    """
    # Create a test project
    project_name = "test-integration"
    project_dir = tmp_path / project_name

    # Initialize TemplateManager with default templates
    template_manager = TemplateManager()

    # Create project with PostgreSQL variant
    result = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name=project_name,
        target_dir=tmp_path,
        variant="postgresql"
    )

    assert result is True
    assert project_dir.exists()

    # Verify essential files exist
    assert (project_dir / "docker-compose.yml").exists()
    assert (project_dir / ".env").exists()

    # Change to project directory
    original_cwd = Path.cwd()
    try:
        # Change to the project directory
        project_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(project_dir)

        # Run docker-compose config to validate
        result = subprocess.run(
            ["docker", "compose", "config"],
            capture_output=True,
            text=True
        )

        # Check that docker-compose config is valid
        assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"

        # Verify the compose configuration contains expected services
        assert "php:" in result.stdout
        assert "postgresql:" in result.stdout
        assert "nginx:" in result.stdout

        # Verify environment variables are properly set
        env_content = (project_dir / ".env").read_text()
        assert "DB_ENGINE=postgresql" in env_content
        assert "DB_PORT=" in env_content
        assert "WEB_PORT=" in env_content
        assert "DB_DATABASE=test-integration" in env_content

        # Verify directory structure
        assert (project_dir / "docker").is_dir()
        assert (project_dir / "docker/postgresql").is_dir()
        assert (project_dir / "docker/nginx").is_dir()

    finally:
        # Restore original working directory
        os.chdir(original_cwd)

        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)
