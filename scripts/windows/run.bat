
REM Define root project directory
call "%~dp0PROJECT_ROOT_DIR.bat"
if not defined PROJECT_ROOT_DIR (
    echo ERROR: Failed to define project root directory.
    exit /b 1
)
set "MAIN_PY_PATH=%PROJECT_ROOT_DIR%\main.py"

REM Navigate to the project root directory.
echo.
echo Navigating to the project root directory '%PROJECT_ROOT_DIR%'...
pushd "%PROJECT_ROOT_DIR%" || (
    echo Error: failed to navigate to the project root directory.
    exit /b 1
)
echo Successfully navigated to the project root directory.

REM Running app
echo.
echo Starting application at '%MAIN_PY_PATH%'...
call python3 "%MAIN_PY_PATH%"
set "EXIT_CODE=%ERRORLEVEL%"

REM Restore the original working directory saved by pushd.
echo.
echo Restoring the original working directory...
popd
if errorlevel 1 (
    echo ERROR: Failed to restore the original working directory.
    set "EXIT_CODE=1"
)
echo Successfully restored the original working directory.

if not "%EXIT_CODE%"=="0" (
    echo ERROR: Application exited with code %EXIT_CODE%.
    exit /b %EXIT_CODE%
)

echo Successfully executed application.
