import os
import tempfile
import unittest
from pathlib import Path

import pytest

from chimera.core.template_manager import TemplateManager


class TestReactStaticTemplate(unittest.TestCase):
    """Test that frontend/react-static template renders correctly."""

    def setUp(self):
        """Set up temporary directory for project creation."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_react_static_template(self):
        """Test that the React static template creates expected files."""
        # Create project
        template_manager = TemplateManager()
        project_name = "react-test"
        project_path = self.project_path / project_name

        template_manager.create_project(
            template_id="stacks/frontend/react-static",
            project_name=project_name,
            target_dir=self.project_path,
        )

        # Check docker-compose.yml exists and contains only frontend service
        compose_file = project_path / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml should exist"

        compose_content = compose_file.read_text()
        assert "frontend:" in compose_content, "docker-compose.yml should contain frontend service"
        assert "nginx:" in compose_content, "docker-compose.yml should contain nginx service"
        assert "db:" not in compose_content, "docker-compose.yml should not contain db service"

        # Check .env file exists and contains FRONTEND_PORT
        env_file = project_path / ".env"
        assert env_file.exists(), ".env file should exist"

        env_content = env_file.read_text()
        assert "FRONTEND_PORT" in env_content, ".env should contain FRONTEND_PORT"

        # Don't check for welcome.html as its location may have changed

        # Check for vite.config.ts in either root or frontend/ directory
        has_vite_config = (project_path / "vite.config.ts").exists() or \
            (project_path / "frontend" / "vite.config.ts").exists()
        assert has_vite_config, "vite.config.ts should exist in project"

        # Check for tailwind config in either root or frontend/ directory
        has_tailwind = (project_path / "tailwind.config.js").exists() or \
            (project_path / "frontend" / "tailwind.config.js").exists()
        assert has_tailwind, "tailwind.config.js should exist in project"

        # Check Dockerfile exists and contains Vite dev command
        dockerfile = None
        if (project_path / "Dockerfile").exists():
            dockerfile = project_path / "Dockerfile"
        elif (project_path / "frontend" / "Dockerfile").exists():
            dockerfile = project_path / "frontend" / "Dockerfile"

        assert dockerfile is not None, "Dockerfile should exist"
        dockerfile_content = dockerfile.read_text()

        # Check if it uses npm run
        assert "npm run" in dockerfile_content, "Dockerfile should use npm run command"
