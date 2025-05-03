import pytest
from pathlib import Path
import shutil
import yaml
from chimera.core import TemplateManager


@pytest.fixture
def template_manager(tmp_path):
    """Create a temporary template manager with test templates."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create a test template structure
    stack_dir = templates_dir / "stacks" / "backend" / "php-web"
    stack_dir.mkdir(parents=True)

    # Create template.yaml
    template_yaml = {
        "name": "PHP Web Backend",
        "description": "PHP web application with database",
        "version": "1.0.0",
        "type": "stack",
        "components": {
            "database": {
                "source": "base/database/${DB_ENGINE}",
                "required": True
            }
        },
        "stack": {
            "type": "backend",
            "default_database": "mysql",
            "supported_databases": [
                {"engine": "mysql", "name": "MySQL", "version": "8.0"},
                {"engine": "postgresql", "name": "PostgreSQL", "version": "14"},
                {"engine": "mariadb", "name": "MariaDB", "version": "10.6"}
            ]
        },
        "welcome_page": {
            "sections": [
                {
                    "title": "Web Server",
                    "service": "nginx",
                    "url": "http://localhost:${WEB_PORT}"
                },
                {
                    "title": "Database",
                    "service": "${DB_ENGINE}",
                    "port": "${DB_PORT}"
                }
            ]
        },
        "files": [
            {
                "source": "docker-compose.${DB_ENGINE}.yml",
                "target": "docker-compose.yml"
            },
            {
                "source": ".env.${DB_ENGINE}.example",
                "target": ".env"
            }
        ],
        "post_copy": [
            {"remove": "docker-compose.mysql.yml"},
            {"remove": "docker-compose.postgresql.yml"},
            {"remove": "docker-compose.mariadb.yml"},
            {"remove": "docker-compose.mysql.override.yml"},
            {"remove": "docker-compose.mariadb.override.yml"},
            {"remove": "docker-compose.postgresql.override.yml"}
        ]
    }

    with open(stack_dir / "template.yaml", "w") as f:
        yaml.dump(template_yaml, f)

    # Create database components
    for db in ["mysql", "postgresql", "mariadb"]:
        db_dir = templates_dir / "base" / "database" / db
        db_dir.mkdir(parents=True)

        # Create docker directory structure
        docker_dir = db_dir / "docker" / db
        docker_dir.mkdir(parents=True)

        # Create a dummy config file
        with open(docker_dir / "config.cnf", "w") as f:
            f.write(f"# {db} configuration")

        # Create component template.yaml
        db_template = {
            "name": f"{db.title()} Database",
            "description": f"{db.title()} database component",
            "version": "1.0.0",
            "type": "component",
            "component": {
                "type": "database",
                "engine": db,
                "version": "latest"
            },
            "config": {
                "port_range": (
                    "3306-3399" if db != "postgresql" else "5432-5632"
                ),
                "env_prefix": "DB"
            },
            "services": {
                "db": {
                    "type": db,
                    "port_range": (
                        "3306-3399" if db != "postgresql" else "5432-5632"
                    ),
                    "required": True,
                    "env_prefix": "DB"
                }
            },
            "files": [
                {
                    "source": "docker",
                    "target": "docker"
                }
            ],
            "environment": {
                "DB_ENGINE": db,
                "DB_HOST": db,
                "DB_PORT": (
                    "3306" if db != "postgresql" else "5432"
                ),
                "DB_DATABASE": "${PROJECT_NAME}",
                "DB_USERNAME": "${PROJECT_NAME}",
                "DB_PASSWORD": "secret",
                "DB_ROOT_PASSWORD": "rootsecret" if db != "postgresql" else None
            }
        }

        # Remove None values from environment
        db_template["environment"] = {
            k: v for k, v in db_template["environment"].items() if v is not None
        }

        # Add post_copy tasks
        post_copy = []
        for other_db in ["mysql", "mariadb", "postgresql"]:
            if other_db != db:
                post_copy.append({"remove_dir": f"docker/{other_db}"})
                post_copy.append({"remove": f"docker-compose.{other_db}.yml"})
        db_template["post_copy"] = post_copy

        with open(db_dir / "template.yaml", "w") as f:
            yaml.dump(db_template, f)

        # Create docker-compose.yml for the database
        db_compose = {
            "version": "3.8",
            "services": {
                db: {
                    "image": f"{db}:latest",
                    "ports": [
                        f"${{DB_PORT}}:{3306 if db != 'postgresql' else 5432}"
                    ],
                    "environment": {
                        "MYSQL_DATABASE": (
                            "${DB_DATABASE}" if db == "mysql" else None
                        ),
                        "MYSQL_USER": (
                            "${DB_USERNAME}" if db == "mysql" else None
                        ),
                        "MYSQL_PASSWORD": (
                            "${DB_PASSWORD}" if db == "mysql" else None
                        ),
                        "MYSQL_ROOT_PASSWORD": (
                            "${DB_ROOT_PASSWORD}" if db == "mysql" else None
                        ),
                        "POSTGRES_DB": (
                            "${DB_DATABASE}" if db == "postgresql" else None
                        ),
                        "POSTGRES_USER": (
                            "${DB_USERNAME}" if db == "postgresql" else None
                        ),
                        "POSTGRES_PASSWORD": (
                            "${DB_PASSWORD}" if db == "postgresql" else None
                        ),
                        "MARIADB_DATABASE": (
                            "${DB_DATABASE}" if db == "mariadb" else None
                        ),
                        "MARIADB_USER": (
                            "${DB_USERNAME}" if db == "mariadb" else None
                        ),
                        "MARIADB_PASSWORD": (
                            "${DB_PASSWORD}" if db == "mariadb" else None
                        ),
                        "MARIADB_ROOT_PASSWORD": (
                            "${DB_ROOT_PASSWORD}" if db == "mariadb" else None
                        ),
                    }
                }
            }
        }

        # Remove None values from environment
        db_compose["services"][db]["environment"] = {
            k: v
            for k, v in db_compose["services"][db]["environment"].items()
            if v is not None
        }

        with open(db_dir / "docker-compose.yml", "w") as f:
            yaml.dump(db_compose, f)

        # Create variant-specific compose file in the stack
        variant_compose = {
            "version": "3.8",
            "services": {
                "php": {
                    "image": "php:8.2-fpm",
                    "environment": {
                        "DB_HOST": db,
                        "DB_PORT": (
                            "3306" if db != "postgresql" else "5432"
                        ),
                        "DB_DATABASE": "${DB_DATABASE}",
                        "DB_USERNAME": "${DB_USERNAME}",
                        "DB_PASSWORD": "${DB_PASSWORD}",
                        "DB_ENGINE": db
                    }
                },
                "web": {
                    "image": "nginx:latest",
                    "ports": ["${WEB_PORT}:80"]
                }
            }
        }
        variant_compose["services"].update(db_compose["services"])

        with open(stack_dir / f"docker-compose.{db}.yml", "w") as f:
            yaml.dump(variant_compose, f)

        # Create .env.example file for the variant
        env_content = f"""DB_ENGINE={db}
DB_HOST={db}
DB_PORT={3306 if db != 'postgresql' else 5432}
DB_DATABASE=${{PROJECT_NAME}}
DB_USERNAME=${{PROJECT_NAME}}
DB_PASSWORD=secret
{'DB_ROOT_PASSWORD=rootsecret' if db != 'postgresql' else ''}
WEB_PORT=8080
"""
        with open(stack_dir / f".env.{db}.example", "w") as f:
            f.write(env_content)

        # Create docker directory structure for the stack
        stack_docker_dir = stack_dir / "docker" / db
        stack_docker_dir.mkdir(parents=True)
        shutil.copy2(
            docker_dir / "config.cnf",
            stack_docker_dir / "config.cnf"
        )

    return TemplateManager(templates_dir=templates_dir)


def test_create_project_basic(template_manager, tmp_path):
    """Test basic project creation without variants."""
    project_dir = tmp_path / "test-project"

    # Create project
    result = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name="test-project",
        target_dir=tmp_path
    )

    assert result is True
    assert project_dir.exists()
    assert (project_dir / "docker-compose.yml").exists()

    # Check if environment variables are set
    env_file = project_dir / ".env"
    assert env_file.exists()
    env_content = env_file.read_text()
    assert "WEB_PORT=" in env_content
    assert "DB_PORT=" in env_content
    assert "DB_DATABASE=test-project" in env_content


@pytest.mark.parametrize("variant", ["mysql", "postgresql", "mariadb"])
def test_create_project_with_variants(template_manager, tmp_path, variant):
    """Test project creation with different database variants."""
    project_dir = tmp_path / f"test-project-{variant}"

    # Create project with variant
    result = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name=f"test-project-{variant}",
        target_dir=tmp_path,
        variant=variant
    )

    assert result is True
    assert project_dir.exists()

    # Check docker-compose.yml
    compose_file = project_dir / "docker-compose.yml"
    assert compose_file.exists()

    with open(compose_file) as f:
        compose = yaml.safe_load(f)

    # Verify database service configuration
    assert variant in compose["services"]

    # Check environment configuration
    env_file = project_dir / ".env"
    assert env_file.exists()
    env_content = env_file.read_text()
    assert f"DB_ENGINE={variant}" in env_content

    # Check port configuration
    if variant == "postgresql":
        assert "5432" in compose["services"][variant]["ports"][0]
    else:
        assert "3306" in compose["services"][variant]["ports"][0]


def test_create_project_with_invalid_variant(template_manager, tmp_path):
    """Test project creation with an invalid variant."""
    result = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name="test-project-invalid",
        target_dir=tmp_path,
        variant="invalid-db"
    )

    assert result is False
    assert not (tmp_path / "test-project-invalid").exists()


def test_create_project_duplicate_directory(template_manager, tmp_path):
    """Test project creation when target directory already exists."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    result = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name="test-project",
        target_dir=tmp_path
    )

    assert result is False


def test_create_project_port_allocation(template_manager, tmp_path):
    """Test that ports are allocated correctly for multiple projects."""
    # Create first project
    result1 = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name="project1",
        target_dir=tmp_path
    )

    assert result1 is True
    env1 = (tmp_path / "project1" / ".env").read_text()
    web_port1 = None
    db_port1 = None

    for line in env1.splitlines():
        if line.startswith("WEB_PORT="):
            web_port1 = line.split("=")[1]
        elif line.startswith("DB_PORT="):
            db_port1 = line.split("=")[1]

    # Create second project
    result2 = template_manager.create_project(
        template_id="stacks/backend/php-web",
        project_name="project2",
        target_dir=tmp_path
    )

    assert result2 is True
    env2 = (tmp_path / "project2" / ".env").read_text()
    web_port2 = None
    db_port2 = None

    for line in env2.splitlines():
        if line.startswith("WEB_PORT="):
            web_port2 = line.split("=")[1]
        elif line.startswith("DB_PORT="):
            db_port2 = line.split("=")[1]

    # Verify ports are different
    assert web_port1 != web_port2
    assert db_port1 != db_port2
