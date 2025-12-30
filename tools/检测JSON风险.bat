@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0.."

set "INPUT=%~1"
if "%INPUT%"=="" (
  echo 用法:
  echo   %~nx0 CSV\CN翻译提取_20251225_202755.csv
  echo.
  set /p INPUT=请输入CSV相对路径^(例如 CSV\CN翻译提取_20251225_202755.csv^): 
)

echo.
echo [1/2] 扫描CSV中可能导致JSON语法错误的内容...
echo 输入: %INPUT%
echo.

python tools\check_csv_json_unsafe.py "%INPUT%" --columns ZH,VN,TH

if errorlevel 1 (
  echo.
  echo 执行失败。请确认:
  echo - 已安装 Python 并已加入 PATH
  echo - 路径输入正确
  pause
  exit /b 1
)

echo.
echo [2/2] 完成。请到 CSV 目录查看 *_json_unsafe_report.csv 报告。
pause
