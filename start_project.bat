@echo off
echo ============================================================
echo   STARTING RADIOLOGY AI DIAGNOSIS SUPPORT SYSTEM
echo ============================================================
echo.

:: Check MongoDB status
echo [*] Checking local MongoDB server...
powershell -Command "Test-NetConnection -ComputerName localhost -Port 27017" | findstr "TcpTestSucceeded"
echo.

:: Start FastAPI Backend
echo [*] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "FastAPI Backend - Radiology AI" cmd /k "cd backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: Start React Frontend
echo [*] Launching React Frontend on http://localhost:5173 ...
start "React Frontend - Radiology AI" cmd /k "cd frontend && npm run dev"

:: Start Telegram Report Bot
echo [*] Launching Telegram Report Bot (Long Polling) ...
start "Telegram Report Bot - Radiology AI" cmd /k "cd backend && venv\Scripts\python.exe -m app.telegram_bot.bot"

echo.
echo ============================================================
echo   System startup initiated!
echo   - Backend:      http://127.0.0.1:8000
echo   - Swagger:      http://127.0.0.1:8000/docs
echo   - Frontend:     http://localhost:5173
echo   - Telegram Bot: Polling Active
echo ============================================================
