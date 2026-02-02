# Homebrew Distribution

Scripts and configuration for distributing metalscribe via Homebrew.

## Files

- `release.sh` — Helper script to update formula after a release

## Usage

### Release a New Version

```bash
# 1. Create git tag and GitHub release
git tag v0.2.0
git push origin v0.2.0
# → Create GitHub release with notes

# 2. Update Homebrew formula
./scripts/homebrew/release.sh v0.2.0

# 3. Commit and push
git add Formula/metalscribe.rb
git commit -m "chore: update formula to v0.2.0"
git push origin main

# 4. Test locally
brew install --build-from-source ./Formula/metalscribe.rb
metalscribe --version

# 5. Clean up
brew uninstall metalscribe
```

## Private Tap

Users can install metalscribe before it's in Homebrew Core:

```bash
# 1. Add tap
brew tap feliperbroering/metalscribe https://github.com/feliperbroering/metalscribe.git

# 2. Install
brew install metalscribe

# 3. Update formula when new versions release
brew update
brew upgrade metalscribe
```

Or create a separate `homebrew-metalscribe` repository if you prefer.

## Homebrew Core Submission

Once metalscribe is stable (3+ releases), submit to Homebrew Core:

1. Create fork of homebrew-core
2. Add `Formula/metalscribe.rb` to your fork
3. Create PR to Homebrew with documentation
4. Respond to maintainer feedback
5. Merge and celebrate! 🎉

See parent repo documentation for full details.
