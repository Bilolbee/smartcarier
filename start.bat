@echo off
echo ========================================
echo    SmartCareer AI - Quick Start
echo ========================================
echo.

:: Check if .env exists
if not exist "backend\.env" (
    echo [!] backend\.env topilmadi!
    echo [!] backend\.env.example dan nusxa oling
    copy backend\.env.example backend\.env
    echo [+] .env fayl yaratildi. OPENAI_API_KEY ni kiriting!
    notepad backend\.env
    pause
)

:: Start Backend
echo [1/2] Backend ishga tushirilmoqda...
cd backend
start cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a bit
timeout /t 5 /nobreak

:: Start Frontend
echo [2/2] Frontend ishga tushirilmoqda...
cd ..\frontend
start cmd /k "npm install && npm run dev"

echo.
echo ========================================
echo    Tayyor!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
pause













