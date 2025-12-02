@echo off
echo Starting AI-Powered Attendance System...

REM Start backend in a new window
start "Attendance Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
start "Attendance Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause >nul

REM Kill the processes
taskkill /FI "WindowTitle eq Attendance Backend*" /F
taskkill /FI "WindowTitle eq Attendance Frontend*" /F
