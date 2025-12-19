@echo off
chcp 65001 >nul
title CSV自动翻译工具 - GUI版本

echo ======================================
echo    CSV自动翻译工具 - GUI版本
echo ======================================
echo.
echo 正在启动图形界面...
echo.

python translate_csv_gui.py

if errorlevel 1 (
    echo.
    echo 启动失败！请确保：
    echo 1. 已安装Python 3.x
    echo 2. 已安装依赖: pip install -r requirements.txt
    echo.
    pause
)
