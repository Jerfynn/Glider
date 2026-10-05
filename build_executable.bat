@echo off
echo ============================================================
echo   Building GliderView Standalone Executable (.exe)
echo ============================================================
echo.

set PYTHON_PATH=C:\Users\jerfi\AppData\Local\Programs\Python\Python313\python.exe
set PYINSTALLER_PATH=C:\Users\jerfi\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

echo Step 1: Building with PyInstaller...
"%PYINSTALLER_PATH%" GliderView.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Standalone folder created at: dist\GliderView\GliderView.exe
echo.

if exist %INNO_PATH% (
    echo Step 2: Compiling Windows Installer with Inno Setup...
    %INNO_PATH% installer_setup.iss
    if errorlevel 1 (
        echo [WARNING] Inno Setup compilation encountered an issue.
    ) else (
        echo [SUCCESS] Windows Installer created at: dist_installer\GliderView_Setup_v1.0.0.exe
    )
) else (
    echo [NOTE] Inno Setup compiler not found at %INNO_PATH%.
    echo You can run dist\GliderView\GliderView.exe directly!
)

echo.
echo ============================================================
echo   Build process completed!
echo ============================================================
pause
