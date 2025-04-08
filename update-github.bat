@echo off
echo Updating GitHub repository...
cd /d %~dp0

git add .
git commit -m "Update website content"
git push

echo.
echo GitHub update complete!
echo Press any key to exit...
pause > nul 