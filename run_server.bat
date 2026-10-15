@echo off
cd "F:\hackathon\Track 2"
start /B python main.py
timeout /T 3 >nul
echo Server starting...