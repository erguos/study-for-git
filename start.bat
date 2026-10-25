@echo off
chcp 65001 >nul
title 智能数据 Agent - 一键启动

echo ============================================
echo   智能数据 Agent 一键启动
echo ============================================
echo 1. 启动后端 (FastAPI, http://localhost:8000)
echo 2. 启动前端 (Vue3,   http://localhost:5173)
echo ============================================

cd /d "%~dp0"

start "backend-data-agent" cmd /k "cd backend && .venv\Scripts\python.exe run.py"
timeout /t 3 /nobreak >nul
start "frontend-data-agent" cmd /k "cd frontend && npm run dev"

echo.
echo 后端已启动: http://localhost:8000  (接口文档 /docs)
echo 前端已启动: http://localhost:5173
echo 默认管理员: admin / admin123
echo.
pause
