#!/bin/bash
# Release metalscribe to Homebrew
# Usage: ./scripts/homebrew/release.sh v0.1.0

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 v0.1.0"
    exit 1
fi

VERSION=$1

# Validate version format (vX.Y.Z)
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format: $VERSION"
    echo "   Version must be in format vX.Y.Z (e.g., v0.1.0, v1.2.3)"
    exit 1
fi
REPO_OWNER="feliperbroering"
REPO_NAME="metalscribe"
REPO="$REPO_OWNER/$REPO_NAME"
TARBALL_URL="https://github.com/${REPO}/archive/refs/tags/${VERSION}.tar.gz"

echo "=========================================="
echo "Release metalscribe to Homebrew"
echo "=========================================="
echo ""
echo "Version: $VERSION"
echo "URL: $TARBALL_URL"
echo ""

# Step 1: Verify version tag exists
echo "Checking if release exists..."
HTTP_STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$TARBALL_URL" 2>/dev/null)
if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Release $VERSION not found (HTTP $HTTP_STATUS)"
    echo "   Did you create the git tag and GitHub release?"
    echo "   URL: $TARBALL_URL"
    exit 1
fi
echo "✓ Release found (HTTP $HTTP_STATUS)"
echo ""

# Step 2: Calculate SHA256
echo "Calculating SHA256..."
SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | awk '{print $1}')
echo "✓ SHA256: $SHA256"
echo ""

# Step 3: Update formula
echo "Updating Formula/metalscribe.rb..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

sed -i '' "s|url \"https://github.com/${REPO}/archive/refs/tags/.*\"|url \"https://github.com/${REPO}/archive/refs/tags/${VERSION}.tar.gz\"|" "$REPO_ROOT/Formula/metalscribe.rb"
sed -i '' "s|sha256 \".*\"|sha256 \"${SHA256}\"|" "$REPO_ROOT/Formula/metalscribe.rb"

echo "✓ Formula updated"
echo ""

# Step 4: Display changes
echo "Changes:"
grep -E "(url|sha256)" "$REPO_ROOT/Formula/metalscribe.rb" | head -2
echo ""

# Step 5: Verify locally
echo "Testing formula locally..."
cd "$REPO_ROOT"
if ! brew audit --strict Formula/metalscribe.rb; then
    echo "⚠️  Formula audit found issues (check above)"
    echo "Continuing anyway..."
fi
echo ""

# Step 6: Summary
echo "=========================================="
echo "✅ Formula Updated"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Commit changes:"
echo "   git add Formula/metalscribe.rb"
echo "   git commit -m 'chore: update formula to $VERSION'"
echo "   git push origin main"
echo ""
echo "2. Test locally:"
echo "   brew install --build-from-source ./Formula/metalscribe.rb"
echo "   metalscribe --version"
echo ""
echo "3. Uninstall and clean up:"
echo "   brew uninstall metalscribe"
echo ""
echo "=========================================="
echo ""
