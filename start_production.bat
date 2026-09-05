@echo off
echo ===================================================
echo Starting AI Warehouse Intelligence Production Server
echo ===================================================
echo Building latest frontend...
cd frontend
call npm run build
cd ..
echo Starting unified server on http://localhost:8000 ...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
