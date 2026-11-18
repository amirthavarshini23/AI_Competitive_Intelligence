@echo off
TITLE AI Competitive Intelligence & Market Strategy Platform Launcher
COLOR 0B

echo ===============================================================================
echo        AI COMPETITIVE INTELLIGENCE & MARKET STRATEGY PLATFORM
echo                     (React 18 + FastAPI + Local NLP + Ollama)
echo ===============================================================================
echo.
echo  [1/2] Launching FastAPI Backend on http://localhost:8000 ...
start "StratIntel Backend (FastAPI)" cmd /k "cd /d D:\Agentic AI\AI_Competitive_Intelligence\backend && python server.py"

echo  [2/2] Launching React Frontend on http://localhost:5173 ...
start "StratIntel Frontend (Vite React)" cmd /k "cd /d D:\Agentic AI\AI_Competitive_Intelligence\frontend && npm run dev"

echo.
echo ===============================================================================
echo  SUCCESS: Both services have been launched in separate terminal windows!
echo.
echo  * Frontend Web Dashboard : http://localhost:5173
echo  * Backend API & Docs     : http://localhost:8000/docs
echo.
echo  Tip: To enable Local Neural LLM generation, start Ollama:
echo       ollama run qwen2.5:3b
echo  (If Ollama is not started, Extractive NLP & Rule-Based mode is used automatically)
echo ===============================================================================
pause
