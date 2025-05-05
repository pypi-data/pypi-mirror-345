import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from chimera.cli import cli


@pytest.fixture
def mock_template_manager():
    """Mock TemplateManager for testing."""
    with patch('chimera.commands.create.TemplateManager') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


def test_create_with_variant_flag(mock_template_manager):
    """Test create command with --variant flag."""
    runner = CliRunner()

    # Test with template and variant options
    result = runner.invoke(
        cli, ["create", "demo", "-t", "stacks/backend/php-web", "-d", "mariadb", "--verbose"])

    assert result.exit_code == 0

    # Verify TemplateManager was called with correct parameters
    mock_template_manager.create_project.assert_called_once_with(
        "stacks/backend/php-web", "demo", variant="mariadb"
    )


def test_create_with_short_variant_flag(mock_template_manager):
    """Test create command with short -d variant flag."""
    runner = CliRunner()

    # Test with short variant flag
    result = runner.invoke(
        cli, ["create", "demo", "-t", "stacks/backend/php-web", "-d", "postgresql"])

    assert result.exit_code == 0

    # Verify TemplateManager was called with correct parameters
    mock_template_manager.create_project.assert_called_once_with(
        "stacks/backend/php-web", "demo", variant="postgresql"
    )


def test_create_without_variant_flag(mock_template_manager):
    """Test create command without variant flag still works."""
    runner = CliRunner()

    # Test without variant flag
    result = runner.invoke(
        cli, ["create", "demo", "-t", "stacks/backend/php-web"])

    assert result.exit_code == 0

    # Verify TemplateManager was called with correct parameters (no variant)
    mock_template_manager.create_project.assert_called_once_with(
        "stacks/backend/php-web", "demo"
    )
