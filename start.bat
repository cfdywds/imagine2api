@echo off
REM Imagine2API - Windows 启动脚本

echo ==================================
echo   Imagine2API - 启动脚本
echo ==================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python 版本:
python --version

REM 检查依赖
echo.
echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少依赖，正在安装...
    pip install -r requirements.txt
) else (
    echo [OK] 依赖已安装
)

REM 检查 key.txt
echo.
if not exist "key.txt" (
    echo [警告] key.txt 文件不存在
    echo 请创建 key.txt 文件并添加 Grok SSO Token
    echo.
    set /p continue="是否继续启动? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [OK] key.txt 文件存在
)

REM 检查 .env
if not exist ".env" (
    echo [警告] .env 文件不存在，将自动创建
)

REM 启动服务
echo.
echo ==================================
echo   启动服务...
echo ==================================
echo.
echo 服务地址: http://localhost:9563
echo API 文档: http://localhost:9563/docs
echo 健康检查: http://localhost:9563/health
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py
