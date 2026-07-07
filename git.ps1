param(
    [Parameter(Mandatory=$true, HelpMessage="Enter your commit message")]
    [string]$CommitMessage
)

# 1. Fetch latest changes and merge them
Write-Host "📥 Pulling latest changes from remote..." -ForegroundColor Cyan
git pull origin main
if ($LASTEXITCODE -ne 0) {
    Write-Error "Git pull failed. Fix conflicts before proceeding."
    exit $LASTEXITCODE
}

# 2. Stage all modifications and new files
Write-Host "➕ Staging all changes..." -ForegroundColor Cyan
git add .

# 3. Commit with the provided message
Write-Host "💾 Committing changes..." -ForegroundColor Cyan
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Nothing to commit or commit failed."
    exit $LASTEXITCODE
}

# 4. Push updates to the main branch
Write-Host "🚀 Pushing changes to origin main..." -ForegroundColor Cyan
git push origin main

Write-Host "✅ Git sync complete!" -ForegroundColor Green
