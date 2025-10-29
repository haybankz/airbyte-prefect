#!/bin/bash
# deploy.sh - Automated deployment script for airbyte-prefect to PyPI
# Usage: ./deploy.sh [test|prod]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_msg "🚀 airbyte-prefect PyPI Deployment Script" "$BLUE"
echo "=========================================="

# Determine target (test or prod)
TARGET="${1:-test}"

if [[ "$TARGET" != "test" && "$TARGET" != "prod" ]]; then
    print_msg "❌ Invalid target. Use 'test' or 'prod'" "$RED"
    echo "Usage: ./deploy.sh [test|prod]"
    exit 1
fi

print_msg "📍 Target: $TARGET" "$YELLOW"
echo ""

# Step 1: Check git status
print_msg "🔍 Checking git status..." "$BLUE"
if [[ -n $(git status --porcelain) ]]; then
    print_msg "⚠️  Warning: You have uncommitted changes" "$YELLOW"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Get current version
CURRENT_VERSION=$(python -c "import versioneer; print(versioneer.get_version())")
print_msg "📦 Current version: $CURRENT_VERSION" "$GREEN"
echo ""

# Step 3: Clean previous builds
print_msg "🧹 Cleaning previous builds..." "$BLUE"
rm -rf dist/ build/ *.egg-info airbyte_prefect.egg-info
print_msg "✓ Build artifacts cleaned" "$GREEN"
echo ""

# Step 4: Build package
print_msg "📦 Building package..." "$BLUE"
python -m build
if [ $? -eq 0 ]; then
    print_msg "✓ Package built successfully" "$GREEN"
else
    print_msg "❌ Build failed!" "$RED"
    exit 1
fi
echo ""

# Step 5: Check the distribution
print_msg "🔍 Checking package distributions..." "$BLUE"
python -m twine check dist/*
if [ $? -eq 0 ]; then
    print_msg "✓ Package checks passed" "$GREEN"
else
    print_msg "❌ Package check failed!" "$RED"
    exit 1
fi
echo ""

# Step 6: Display package contents
print_msg "📋 Distribution files:" "$BLUE"
ls -lh dist/
echo ""

# Step 7: Upload based on target
if [ "$TARGET" == "test" ]; then
    print_msg "🧪 Uploading to TestPyPI..." "$YELLOW"
    echo ""
    read -p "Continue with TestPyPI upload? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m twine upload --repository testpypi dist/* --verbose
        if [ $? -eq 0 ]; then
            print_msg "✅ Successfully uploaded to TestPyPI!" "$GREEN"
            echo ""
            print_msg "📍 View at: https://test.pypi.org/project/airbyte-prefect/" "$BLUE"
            echo ""
            print_msg "Test installation:" "$YELLOW"
            echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ airbyte-prefect"
        else
            print_msg "❌ Upload to TestPyPI failed!" "$RED"
            exit 1
        fi
    else
        print_msg "❌ Upload cancelled" "$YELLOW"
        exit 0
    fi
elif [ "$TARGET" == "prod" ]; then
    print_msg "🎯 Uploading to Production PyPI..." "$YELLOW"
    echo ""
    print_msg "⚠️  WARNING: This will upload to PRODUCTION PyPI!" "$RED"
    read -p "Are you sure you want to continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m twine upload dist/*
        if [ $? -eq 0 ]; then
            print_msg "✅ Successfully uploaded to PyPI!" "$GREEN"
            echo ""
            print_msg "📍 View at: https://pypi.org/project/airbyte-prefect/" "$BLUE"
            echo ""
            print_msg "Install with:" "$YELLOW"
            echo "pip install airbyte-prefect"
            echo ""
            print_msg "🎉 Deployment complete!" "$GREEN"
        else
            print_msg "❌ Upload to PyPI failed!" "$RED"
            exit 1
        fi
    else
        print_msg "❌ Upload cancelled" "$YELLOW"
        exit 0
    fi
fi

echo ""
print_msg "✨ All done!" "$GREEN"
