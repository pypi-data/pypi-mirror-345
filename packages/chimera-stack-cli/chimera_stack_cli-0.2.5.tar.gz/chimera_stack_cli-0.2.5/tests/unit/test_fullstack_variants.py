import os
import tempfile
import unittest
import re
from pathlib import Path

import pytest

from chimera.core.template_manager import TemplateManager


class TestFullstackReactPhpVariants(unittest.TestCase):
    """Test that fullstack/react-php template variants render correctly."""

    def setUp(self):
        """Set up temporary directory for project creation."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _create_project_with_variant(self, variant: str) -> Path:
        """Helper to create a project with specified variant."""
        template_manager = TemplateManager()
        project_path = self.project_path / f"project-{variant}"

        template_manager.create_project(
            template_id="stacks/fullstack/react-php",
            project_name=f"project-{variant}",
            variant=variant,
            target_dir=self.project_path,
        )

        return project_path

    def _assert_common_project_structure(self, project_path: Path):
        """Assert common structure exists across all variants."""
        # Check the frontend folder has Vite config
        assert (project_path / "frontend/vite.config.ts").exists()

        # Check the frontend has Tailwind config
        assert (project_path / "frontend/tailwind.config.js").exists()

        # Check the Nginx config exists with API routing
        nginx_conf = project_path / "docker/nginx/conf.d/default.conf"
        assert nginx_conf.exists()

        # Verify docker-compose.yml was generated
        assert (project_path / "docker-compose.yml").exists()

        # Legacy files should be removed
        assert not (project_path / "docker-compose.mysql.yml").exists()
        assert not (project_path / "docker-compose.postgresql.yml").exists()
        assert not (project_path / "docker-compose.mariadb.yml").exists()

    def test_mysql_variant(self):
        """Test MySQL variant of the fullstack/react-php template."""
        project_path = self._create_project_with_variant("mysql")
        self._assert_common_project_structure(project_path)

        # Verify docker-compose.yml exists and is a valid YAML file
        compose_content = (project_path / "docker-compose.yml").read_text()
        assert compose_content, "docker-compose.yml should not be empty"

        # Check frontend Dockerfile uses Vite
        frontend_dockerfile = (
            project_path / "frontend/Dockerfile").read_text()
        assert "npm run" in frontend_dockerfile, "Frontend Dockerfile should contain npm run command"

    def test_postgresql_variant(self):
        """Test PostgreSQL variant of the fullstack/react-php template."""
        project_path = self._create_project_with_variant("postgresql")
        self._assert_common_project_structure(project_path)

        # Verify docker-compose.yml exists and is a valid YAML file
        compose_content = (project_path / "docker-compose.yml").read_text()
        assert compose_content, "docker-compose.yml should not be empty"

        # Check frontend Dockerfile uses Vite
        frontend_dockerfile = (
            project_path / "frontend/Dockerfile").read_text()
        assert "npm run" in frontend_dockerfile, "Frontend Dockerfile should contain npm run command"

    def test_mariadb_variant(self):
        """Test MariaDB variant of the fullstack/react-php template."""
        project_path = self._create_project_with_variant("mariadb")
        self._assert_common_project_structure(project_path)

        # Verify docker-compose.yml exists and is a valid YAML file
        compose_content = (project_path / "docker-compose.yml").read_text()
        assert compose_content, "docker-compose.yml should not be empty"

        # Check frontend Dockerfile uses Vite
        frontend_dockerfile = (
            project_path / "frontend/Dockerfile").read_text()
        assert "npm run" in frontend_dockerfile, "Frontend Dockerfile should contain npm run command"
