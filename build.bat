@echo off
chcp 65001 >nul
echo ==========================================
echo   Strix 打包工具
echo ==========================================
echo.

REM 检查 pyinstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    pip install pyinstaller -q
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
)

echo [1/3] 清理旧文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Strix.spec" del "Strix.spec"

echo [2/3] 打包中...这可能需要几分钟
echo.

pyinstaller ^
    --name=Strix ^
    --windowed ^
    --onefile ^
    --icon=resources\strix.ico ^
    --add-data="resources;resources" ^
    --add-data="plugins;plugins" ^
    --clean ^
    --noconfirm ^
    strix.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo.
echo ==========================================
echo   输出文件: dist\Strix.exe
echo ==========================================
echo.
pause
