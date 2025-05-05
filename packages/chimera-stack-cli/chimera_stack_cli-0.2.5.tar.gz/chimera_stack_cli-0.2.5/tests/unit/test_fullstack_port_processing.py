import pytest
from pathlib import Path
from chimera.core import TemplateManager


def test_fullstack_react_php_creation(tmp_path):
    """Test that fullstack react-php template can be created without errors."""
    tm = TemplateManager()
    # Create the project and verify it succeeds
    result = tm.create_project(
        "stacks/fullstack/react-php", "demo", target_dir=tmp_path, variant="mysql")

    # Assert the creation was successful
    assert result is True

    # Verify key files exist
    assert (tmp_path / "demo" / "docker-compose.yml").exists()
    assert (tmp_path / "demo" / ".env").exists()

    # Check README has port variables substituted
    readme = (tmp_path / "demo" / "README.md").read_text()
    # Ports should be visible, not as ${PORT_NAME}
    assert "localhost:" in readme
