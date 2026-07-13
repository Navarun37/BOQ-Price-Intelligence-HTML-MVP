@echo off
rem BOQ Price Finder — double-click to run (Windows)
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
start "" http://127.0.0.1:5544
python server.py
pause
