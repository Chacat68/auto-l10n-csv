@echo off
chcp 65001 >nul
title CSV自动翻译工具 - 安装Electron依赖

echo ======================================
echo    安装Electron依赖
echo ======================================
echo.
echo 正在安装Node.js依赖包...
echo.

npm install

if errorlevel 1 (
    echo.
    echo 安装失败！请检查：
    echo 1. 是否已安装Node.js
    echo 2. npm是否正常工作
    echo.
) else (
    echo.
    echo ======================================
    echo    安装完成！
    echo ======================================
    echo.
    echo 现在可以双击"启动Electron.bat"运行程序
    echo.
)

pause
