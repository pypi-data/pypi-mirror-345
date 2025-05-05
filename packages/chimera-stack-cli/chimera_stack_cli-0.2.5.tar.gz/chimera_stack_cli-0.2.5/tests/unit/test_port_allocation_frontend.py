import pytest
from pathlib import Path
from chimera.core import TemplateManager


def test_frontend_only_ports(tmp_path):
    """Test that frontend-only templates only get frontend ports allocated."""
    tm = TemplateManager()
    tm.create_project("stacks/frontend/react-static",
                      "demo", target_dir=tmp_path)
    env = (tmp_path / "demo" / ".env").read_text()

    # Frontend port should be present
    assert "FRONTEND_PORT" in env

    # Database-related ports should not be present
    assert "DB_PORT" not in env
    assert "MYSQL_PORT" not in env
    assert "POSTGRESQL_PORT" not in env
    assert "MARIADB_PORT" not in env

    # Admin port should not be present
    assert "ADMIN_PORT" not in env
    assert "PGADMIN_PORT" not in env
    assert "PHPMYADMIN_PORT" not in env


def test_backend_still_gets_db_ports(tmp_path):
    """Test that backend templates still get database ports allocated."""
    tm = TemplateManager()
    tm.create_project("stacks/backend/php-web", "demo",
                      target_dir=tmp_path, variant="mysql")
    env = (tmp_path / "demo" / ".env").read_text()

    # Web port should be present
    assert "WEB_PORT" in env

    # Database port should be present
    assert "DB_PORT" in env
    assert "MYSQL_PORT" in env

    # Admin port should be present
    assert "ADMIN_PORT" in env
    assert "PHPMYADMIN_PORT" in env
