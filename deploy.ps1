# PERI GCB Site Auto-Deployer (PowerShell)
# Pushes all 177 generated HTML files to GitHub in one atomic commit

$ErrorActionPreference = "Stop"

$REPO_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $REPO_DIR

# Verify we're in the right place
if (-not (Test-Path "index.html")) {
    Write-Host "❌ Error: index.html not found. Are you in the site directory?" -ForegroundColor Red
    exit 1
}

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "🔧 Initializing git repository..." -ForegroundColor Yellow
    git init
    git config user.email "kiminanoliu@gmail.com"
    git config user.name "Kimi Liu"
    git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git
    git branch -M main
}

# Check that origin is set correctly
try {
    $origin = git remote get-url origin
    if ($origin -notmatch "peri-gcb") {
        Write-Host "⚠️  Remote origin not configured correctly. Setting it now..." -ForegroundColor Yellow
        git remote remove origin 2>$null
        git remote add origin https://github.com/kiminanoliu-eng/peri-gcb.git
    }
} catch {}

# Stage all files
Write-Host "📁 Staging all files..." -ForegroundColor Green
git add -A

# Check what we're committing
$files = (git diff --cached --name-only | Measure-Object -Line).Lines
Write-Host "   Found $files files to commit" -ForegroundColor Green

if ($files -eq 0) {
    Write-Host "ℹ️  No changes to commit (everything is already up to date)" -ForegroundColor Cyan
    exit 0
}

# Create commit
Write-Host "💾 Creating commit..." -ForegroundColor Green
git commit -m "Add GCB PERI product hub — 165 product pages, 12 category pages, homepage"

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host "✅ SUCCESS! All files pushed to GitHub." -ForegroundColor Green
Write-Host "🌐 Site will be live at: https://kiminanoliu-eng.github.io/peri-gcb/" -ForegroundColor Cyan
Write-Host "   (GitHub Pages build takes ~1-2 minutes)" -ForegroundColor Cyan
