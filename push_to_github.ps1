# Initialize
try { git init } catch { }

# Add files
git add .

# Commit
git commit -m "Initial commit - Multi-Camera People Counting System"

# Branch
git branch -M main

# Remote (Remove old if exists to avoid error)
try { git remote remove origin } catch { }
# Add new
git remote add origin https://github.com/Maz1ar-A1i/shaadihaal_counting.git

# Push
Write-Host "Pushing to GitHub..."
git push -u origin main
Write-Host "Done."
