#!/bin/bash
# PERI GCB Site Auto-Deployer
# Pushes all 177 generated HTML files to GitHub in one atomic commit

set -e  # Exit on any error

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Verify we're in the right place
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Are you in the site directory?"
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git config user.email "kiminanoliu@gmail.com"
    git config user.name "Kimi Liu"
    git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git
    git branch -M main
fi

# Check that origin is set correctly
if ! git remote get-url origin | grep -q "peri-gcb"; then
    echo "⚠️  Remote origin not configured correctly. Setting it now..."
    git remote remove origin 2>/dev/null || true
    git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git
fi

# Stage all files
echo "📁 Staging all files..."
git add -A

# Check what we're committing
FILE_COUNT=$(git diff --cached --name-only | wc -l)
echo "   Found $FILE_COUNT files to commit"

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "ℹ️  No changes to commit (everything is already up to date)"
    exit 0
fi

# Create commit
echo "💾 Creating commit..."
git commit -m "Add GCB PERI product hub — 165 product pages, 12 category pages, homepage"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo "✅ SUCCESS! All files pushed to GitHub."
echo "🌐 Site will be live at: https://kiminanoliu-eng.github.io/peri-gcb/"
echo "   (GitHub Pages build takes ~1-2 minutes)"
