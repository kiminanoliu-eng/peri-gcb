#!/bin/bash
# PERI GCB Auto-Deploy Script
# This script pushes all website files to GitHub

cd "$(dirname "$0")"
echo "================================================"
echo "  PERI GCB Website — Auto Deploy to GitHub"
echo "================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Download: https://git-scm.com/download/mac"
    read -p "Press Enter to close..."
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git config user.email "kiminanoliu@gmail.com"
    git config user.name "Kimi Liu"
    git branch -M main
fi

# Set remote
git remote remove origin 2>/dev/null
git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git

# Stage all HTML files
echo ""
echo "📁 Staging all website files..."
git add index.html categories/ products/ 2>/dev/null
git add -A

FILE_COUNT=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $FILE_COUNT files to commit"

if [ "$FILE_COUNT" -eq 0 ] || [ "$FILE_COUNT" = "0" ]; then
    echo "ℹ️  No new changes to commit."
    echo "   Trying to push existing commits..."
    git push -u origin main 2>&1
    echo ""
    echo "✅ Done! Check: https://kiminanoliu-eng.github.io/peri-gcb/"
    read -p "Press Enter to close..."
    exit 0
fi

# Commit
echo ""
echo "💾 Creating commit..."
git commit -m "Add GCB PERI product hub — 165 product pages, 12 category pages, homepage"

# Push
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main 2>&1

echo ""
echo "================================================"
echo "  ✅ SUCCESS! Website deployed to GitHub!"
echo "  🌐 https://kiminanoliu-eng.github.io/peri-gcb/"
echo "  ⏱️  Wait 1-2 minutes for GitHub Pages to build"
echo "================================================"
echo ""
read -p "Press Enter to close this window..."
