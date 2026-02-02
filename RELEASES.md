# Release Guide

How to release metalscribe to users via Homebrew.

## Release Checklist

Before releasing:

- [ ] All tests passing: `pytest tests/`
- [ ] Linting clean: `ruff check src/`
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Documentation up-to-date
- [ ] No `TODO` or `FIXME` in core code

## Release Process

### 1. Create Git Tag & GitHub Release

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0: [feature description]"

# Push tag to GitHub
git push origin v0.2.0

# Go to GitHub and create release with notes:
# https://github.com/feliperbroering/metalscribe/releases/new
```

### 2. Update Homebrew Formula

```bash
# Use helper script
./scripts/homebrew/release.sh v0.2.0

# Or manually:
# - Copy new SHA256 from script output
# - Update Formula/metalscribe.rb
# - Update version number if needed
```

### 3. Commit & Push

```bash
git add Formula/metalscribe.rb
git commit -m "chore: update formula to v0.2.0"
git push origin main
```

### 4. Test Locally

```bash
# Test Homebrew formula
brew install --build-from-source ./Formula/metalscribe.rb
metalscribe --version

# Verify functionality
metalscribe doctor --check-only

# Cleanup
brew uninstall metalscribe
```

### 5. Verify CI/CD

- Check GitHub Actions: `.github/workflows/homebrew-test.yml`
- Should test on macOS 13, 14, 15
- All tests should pass

## Versioning

Follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes to CLI or output format
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes

Examples:
- `v0.1.0` → Initial release
- `v0.1.1` → Bug fix
- `v0.2.0` → New feature (diarization improvements)
- `v1.0.0` → Stable API, ready for production

## Publishing to Homebrew Core

After 3-6 months with stable releases:

1. See `HOMEBREW_TECHSPEC.md` in workspace
2. Create PR to `homebrew-core`
3. Wait for review & merge
4. Users install with: `brew install metalscribe` (no tap needed)

## Troubleshooting

### Formula test fails locally

```bash
# Debug with verbose output
brew install -s -v metalscribe

# Check formula syntax
brew audit --strict Formula/metalscribe.rb

# Verify dependencies
brew list python@3.11
brew list ffmpeg
```

### SHA256 mismatch

```bash
# Recalculate SHA256
curl -sL https://github.com/feliperbroering/metalscribe/archive/refs/tags/v0.2.0.tar.gz | shasum -a 256

# Update formula manually
sed -i '' 's/sha256 ".*"/sha256 "new_hash"/g' Formula/metalscribe.rb
```

### GitHub Actions failing

- Check `.github/workflows/homebrew-test.yml` logs
- Common issues:
  - Python path incorrect
  - ffmpeg not installed
  - venv creation failed
- Check if macOS version is supported (Ventura 13+)

## Questions?

See:
- `scripts/homebrew/README.md` — Helper scripts
- `.github/workflows/homebrew-test.yml` — CI/CD config
- `HOMEBREW_TECHSPEC.md` (workspace) — Full Homebrew guide
