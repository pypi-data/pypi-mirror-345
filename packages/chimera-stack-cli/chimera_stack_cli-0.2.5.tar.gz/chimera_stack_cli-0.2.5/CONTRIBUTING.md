# Contributing to ChimeraStack CLI

This guide is for developers who want to contribute to the ChimeraStack CLI project.

## Development Environment Setup

### Option 1: Using Docker (Recommended)

This is the recommended approach as it ensures a consistent development environment across all platforms.

1. Clone the repository:

```bash
git clone https://github.com/Amirofcodes/ChimeraStack_CLI.git
cd ChimeraStack_CLI
```

2. Start the development container:

```bash
docker-compose up -d
```

3. Access the development container:

```bash
docker exec -it chimerastack_cli-cli-dev-1 bash
```

4. Install the package in development mode:

```bash
pip install -e .
```

### Option 2: Local Development

If you prefer developing directly on your machine:

1. Prerequisites:

   - Python 3.11+
   - pip
   - virtualenv or venv

2. Clone and setup:

```bash
# Clone the repository
git clone https://github.com/Amirofcodes/ChimeraStack_CLI.git
cd ChimeraStack_CLI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and package in development mode
pip install -r requirements.txt
pip install -e .
```

## Development Commands

### Testing Templates

```bash
# Create test project
chimera create test-project

# Show template selection menu
chimera create --help

# List available templates
chimera list

# Verify template structure
tree -a test-project

# Test container setup
cd test-project
docker-compose config
docker-compose up -d
```

### Common Development Tasks

```bash
# Run tests
pytest

# Format code
black src/

# Check types
mypy src/

# Build package
python setup.py build
```

## Project Structure

```
ChimeraStack_CLI/
├── docker-compose.yml      # Development container configuration
├── Dockerfile             # Python development environment
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── src/
│   └── chimera/
│       ├── cli.py         # CLI entry point
│       ├── commands/      # Command implementations
│       │   ├── create.py  # Project creation logic
│       │   └── list.py    # Template listing logic
│       ├── core/          # Core business logic
│       │   └── template_manager.py  # Template handling
│       ├── templates/     # Project templates
│       │   ├── php/
│       │   │   └── nginx/
│       │   │       ├── mysql/
│       │   │       ├── postgresql/
│       │   │       └── mariadb/
│       │   └── fullstack/
│       │       └── react-php/
│       │           └── mysql-nginx/
│       └── utils/         # Helper functions
└── tests/                # Test suite
```

## Template Development

Looking to **build or extend templates**? We moved the full authoring guide to:

➡️ `docs/authoring-templates.md`

That document covers schema, best-practices and publishing workflow.

👉 **Important**: Be sure to declare a `welcome_page.sections` entry for **every exposed service/port** (e.g. `web`, `db`, `admin`, `frontend`).
The CLI uses these sections to print the dynamic "Port Allocations / Next steps / Access your environment" summary after `chimera create`.

## Commit Guidelines

We follow semantic versioning for commits:

```
feat: Add new feature
fix: Bug fix
docs: Documentation changes
style: Code style updates
refactor: Code refactoring
test: Test updates
chore: Routine tasks
```

Example commit messages:

```
feat: add PostgreSQL template
docs: update template development guide
fix: resolve MariaDB connection issue
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit with semantic versioning (`git commit -m 'feat: add amazing feature'`)
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Questions and Support

- Create an issue for bugs or feature requests
- Join development discussions
- Check existing documentation and issues before posting

## License

This project is licensed under the MIT License - see the LICENSE file for details.
