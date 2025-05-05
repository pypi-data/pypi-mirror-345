# Changelog

All notable changes to ChimeraStack CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.3] - 2024-03-27

### Fixed

- Corrected GitHub repository URL in package metadata

## [v0.2.2] - 2024-03-27

### Added

- Added missing jinja2 dependency

## [v0.2.1] - 2024-03-27

### Added

- Added missing jsonschema dependency

## [v0.2.0] - 2024-03-27

### Added

- Initial release with basic template functionality
- Support for PHP web development templates
- Docker-based development environments
- Template validation using JSON Schema
- Command-line interface for project creation and management

### Changed

- Standardized directory and naming conventions to kebab-case
- Migrated from string replacement to Jinja2 templating
- Flattened compose generation logic
- Improved cleanup mechanisms with per-component tasks

### Removed

- Legacy string replacement template processing
- Ad-hoc port allocation scanning
- Monolithic cleanup function
- Stray .override and .base compose files

### Fixed

- Port allocation conflicts through dedicated config
- Template validation with helpful error messages
- Component cleanup process reliability
- Documentation gaps for template authors

[v0.2.0]: https://github.com/amirofcodes/ChimeraStack-CLI/releases/tag/v0.2.0
