# Git commit and push script for production-ready release (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Git Commit & Push Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if we're on the right branch
$CURRENT_BRANCH = git branch --show-current
Write-Host "Current branch: $CURRENT_BRANCH" -ForegroundColor Yellow

if ($CURRENT_BRANCH -ne "GEMINI_API_PROD_READY") {
    Write-Host "Warning: Not on GEMINI_API_PROD_READY branch" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Stage all changes
Write-Host ""
Write-Host "Staging all changes..." -ForegroundColor Green
git add -A

# Show status
Write-Host ""
Write-Host "Changes to be committed:" -ForegroundColor Cyan
git status --short

# Read commit message
$commitMessage = Get-Content COMMIT_MESSAGE.txt -Raw

# Commit
Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Green
git commit -m $commitMessage

# Push
Write-Host ""
Write-Host "Pushing to remote..." -ForegroundColor Green
git push origin $CURRENT_BRANCH

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Done! Changes pushed to GitHub" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: https://github.com/ArtemRivnyi/ai-ticket-classifier/tree/GEMINI_API_PROD_READY" -ForegroundColor Blue

