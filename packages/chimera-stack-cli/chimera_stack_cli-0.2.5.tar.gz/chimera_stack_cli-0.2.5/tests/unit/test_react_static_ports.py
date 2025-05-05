import pytest
from pathlib import Path
from chimera.core import TemplateManager


def test_react_static_ports(tmp_path):
    """Test that react-static templates get both frontend and web ports but no database ports."""
    tm = TemplateManager()
    tm.create_project("stacks/frontend/react-static",
                      "site", target_dir=tmp_path)
    env = (tmp_path / "site" / ".env").read_text()

    # Frontend port should be present
    assert "FRONTEND_PORT=" in env

    # Web port should be present for nginx
    assert "WEB_PORT=" in env

    # Database-related ports should not be present
    assert "DB_PORT" not in env
    assert "MYSQL_PORT" not in env
    assert "POSTGRESQL_PORT" not in env

    # Admin port should not be present
    assert "ADMIN_PORT" not in env
    assert "PGADMIN_PORT" not in env
    assert "PHPMYADMIN_PORT" not in env

    # Check that docker-compose.yml has correct network configuration
    compose = (tmp_path / "site" / "docker-compose.yml").read_text()
    assert "networks:" in compose
    assert "app_network:" in compose
    assert "name: site_network" in compose
    assert "networks:\n    - app_network" in compose  # indentation in YAML matters
