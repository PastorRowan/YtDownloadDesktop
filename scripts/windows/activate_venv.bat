
@echo off

call "%~dp0PROJECT_ROOT_DIR.bat"

REM Defines the Python virtual environment activation script.
set VENV_ACTIVATION_SCRIPT_FILE=%PROJECT_ROOT_DIR%\venv\Scripts\activate

REM Navigate to the project root directory.
echo.
echo Navigating to the project root directory at '%PROJECT_ROOT_DIR%'...
pushd "%PROJECT_ROOT_DIR%" || (
    echo "Error: failed to navigate to '%PROJECT_ROOT_DIR%'"
    exit /b 1
)
echo Successfully navigated to the project root directory.

REM Activate virtual enviroment
echo.
echo Activating virtual enviroment...
echo Checking if if virtual environment activation script exists at '%VENV_ACTIVATION_SCRIPT_FILE%'.
if exist "%VENV_ACTIVATION_SCRIPT_FILE%" (
    echo Found activation script, activating virtual enviroment.
    call "%VENV_ACTIVATION_SCRIPT_FILE%"
    if errorlevel 1 (
        echo Error: failed to run activation script.
        popd
        exit /b 1
    )
) else (
    echo ERROR: Failed to find activation script.
    popd
    exit /b 1
)
echo Successfully activated virtual enviroment.

REM Restore the original working directory saved by pushd.
echo.
echo Restoring the original working directory...
popd
if errorlevel 1 (
    echo ERROR: Failed to restore the original working directory.
    exit /b 1
)
echo Succesfully restored the original working directory.
