@echo off
chcp 65001 >nul
title CSV自动翻译工具 - 安装依赖

echo ======================================
echo    CSV自动翻译工具 - 安装依赖
echo ======================================
echo.
echo 正在安装Python依赖包...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败！请检查：
    echo 1. 是否已安装Python 3.x
    echo 2. pip是否正常工作
    echo.
) else (
    echo.
    echo ======================================
    echo    安装完成！
    echo ======================================
    echo.
    echo 现在可以双击"启动GUI.bat"运行程序
    echo.
)

pause
