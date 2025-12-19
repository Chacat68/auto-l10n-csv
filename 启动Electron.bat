@echo off
chcp 65001 >nul
title CSV自动翻译工具 - Electron版本

echo ======================================
echo    CSV自动翻译工具 - Electron版本
echo ======================================
echo.
echo 正在启动Electron应用...
echo.

npm start

if errorlevel 1 (
    echo.
    echo 启动失败！请确保：
    echo 1. 已安装Node.js
    echo 2. 已安装依赖: npm install
    echo.
    pause
)
