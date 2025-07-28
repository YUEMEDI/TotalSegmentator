@echo off
echo ========================================
echo ADDING USERS TO YUETRANSFER
echo ========================================
echo.

cd /d "D:\Github\TotalSegmentator\yuetransfer"

echo Running add_users.py...
C:\Users\ZERO\.conda\envs\totalsegmentator\python.exe add_users.py

echo.
echo ========================================
echo USER ADDITION COMPLETE
echo ========================================
echo.
echo Available users:
echo - pokpok / pokpok (Admin)
echo - aaa / aaa (User)
echo - bbb / bbb (User)
echo - ccc / ccc (User)
echo.
pause 