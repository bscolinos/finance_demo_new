@echo off
REM AI Financial Advisor - Development Environment Startup Script (Windows)
REM This script starts all required services in separate command prompt windows

echo 🚀 Starting AI Financial Advisor Development Environment...
echo ==================================================

REM Check if we're in the correct directory
if not exist "dash_app.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo    ^(The directory containing dash_app.py^)
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo ⚠️  Warning: Virtual environment not found at backend\venv
    echo    Please run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    set /p continue_anyway="Continue anyway? (y/N): "
    if /i not "%continue_anyway%"=="y" (
        exit /b 1
    )
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ⚠️  Warning: Node modules not found at frontend\node_modules
    echo    Please run: cd frontend ^&^& npm install
    set /p continue_anyway="Continue anyway? (y/N): "
    if /i not "%continue_anyway%"=="y" (
        exit /b 1
    )
)

echo 📊 Starting Backend API Server...
start "Backend API - http://localhost:8000" cmd /k "cd /d %cd%\backend && echo 🔥 Backend API Starting... && venv\Scripts\activate && echo Backend starting on http://localhost:8000 && python run.py"

timeout /t 3 /nobreak >nul

echo ⚛️  Starting Frontend React App...
start "Frontend React - http://localhost:3000" cmd /k "cd /d %cd%\frontend && echo 🔥 Frontend React Starting... && echo Frontend starting on http://localhost:3000 && npm start"

timeout /t 3 /nobreak >nul

echo 📈 Starting Dash Analytics Dashboard...
start "Dash App - http://localhost:8050" cmd /k "cd /d %cd% && echo 🔥 Dash App Starting... && backend\venv\Scripts\activate && echo Dash app starting on http://localhost:8050 && python dash_app.py"

timeout /t 3 /nobreak >nul

echo 🔄 Starting Streaming Service...
start "Streaming Service" cmd /k "cd /d %cd%\streaming && echo 🔥 Streaming Service Starting... && ..\backend\venv\Scripts\activate && echo Streaming service starting... && python main.py"

echo.
echo ✅ All services are starting up!
echo ==================================================
echo 🌐 Access URLs:
echo    Frontend:      http://localhost:3000
echo    Backend API:   http://localhost:8000
echo    API Docs:      http://localhost:8000/docs
echo    Dash App:      http://localhost:8050
echo.
echo 📋 Check the individual command prompt windows for detailed logs
echo 🛑 To stop all services: Close the command prompt windows or press Ctrl+C in each
echo.
echo 🎉 Happy developing!
echo.
pause 