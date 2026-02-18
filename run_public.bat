@echo off
setlocal
echo ==========================================
echo   College Voting System - PUBLIC MODE
echo ==========================================
echo.
echo 1. Getting your Public Tunnel URL...

start /b python manage.py runserver 0.0.0.0:8001 > server_log.txt 2>&1
echo Server starting on port 8001...

echo.
echo IMPORTANT: When you open the link, it might ask for a "Tunnel Password".
echo Your Tunnel Password/Endpoint IP is: 
curl -4 ifconfig.me
echo.
echo.
echo Launching tunnel...
npx -y localtunnel --port 8001
pause
