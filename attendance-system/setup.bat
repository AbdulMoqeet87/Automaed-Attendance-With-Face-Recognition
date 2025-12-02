@echo off
echo ========================================
echo  AI-Powered Attendance System Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    exit /b 1
)

REM Check MongoDB
echo Checking MongoDB...
sc query MongoDB >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: MongoDB service not found. Make sure MongoDB is installed.
)

echo.
echo Setting up Backend...
cd backend

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Create .env file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

REM Initialize database
echo Initializing database...
python init_db.py

cd ..

echo.
echo Setting up Frontend...
cd frontend

REM Install npm dependencies
echo Installing Node.js dependencies...
call npm install

cd ..

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Start MongoDB (if not running)
echo   2. Run backend:  cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo   3. Run frontend: cd frontend ^&^& npm start
echo.
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:3000
echo.

pause
