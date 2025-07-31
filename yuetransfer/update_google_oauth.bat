@echo off
echo 🔧 Google OAuth Credentials Updater
echo ================================================
echo.
echo This script will help you update your Google OAuth credentials
echo in the YueTransfer server.
echo.
echo Make sure you have your Google Client ID and Client Secret ready!
echo.
pause

C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe update_google_oauth.py

echo.
echo Press any key to exit...
pause >nul