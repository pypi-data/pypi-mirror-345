# Release Workflow Checklist

## Pre-Release Checks

- [ ] All tests passing locally: `pytest -m "not integration" -q`
- [ ] All pre-commit hooks passing: `pre-commit run --all-files`
- [ ] Documentation is up to date

## Local Changes

- [ ] Update version in `src/chimera/__init__.py`
- [ ] Update version in `setup.py`
- [ ] Update version in `Dockerfile.test`
- [ ] Update CHANGELOG.md with new version and changes

## Build and Test Locally

- [ ] Clean previous builds: `rm -rf build/ dist/`
- [ ] Build package: `python -m build`
- [ ] Build macOS executable: `./build_executables.sh`
- [ ] Build Linux executable: `docker build -t chimera-build -f Dockerfile.build .`
- [ ] Extract Linux executable: `docker cp $(docker create chimera-build):/app/dist/chimera-stack-cli ./releases/chimera-stack-cli-linux`
- [ ] Test macOS executable: `./releases/chimera-stack-cli --version`
- [ ] Test Linux executable in Docker: `docker run --rm -v $(pwd)/releases:/test ubuntu /test/chimera-stack-cli-linux --version`

## Git Operations

- [ ] Commit all changes: `git add . && git commit -m "fix: description of changes"`
- [ ] Create git tag: `git tag v{version}`
- [ ] Push tag: `git push origin v{version}`
- [ ] Push all changes: `git push origin main`

## GitHub Release

- [ ] Create GitHub release with tag
- [ ] Upload macOS and Linux executables to release
- [ ] Add release notes from CHANGELOG.md
- [ ] Publish release

## PyPI Deployment

- [ ] Upload to PyPI: `python -m twine upload dist/*`
- [ ] Verify package on PyPI: https://pypi.org/project/chimera-stack-cli/
- [ ] Test installation: `pipx install chimera-stack-cli=={version} --force`

## Post-Release Verification

- [ ] Verify executables work on both platforms
- [ ] Update documentation if needed
- [ ] Close related issues and PRs
