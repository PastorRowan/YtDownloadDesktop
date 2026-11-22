
@echo off

REM Defines the absolute, normalized path to the project root directory.
for %%I in ("%~dp0..\..") do set "PROJECT_ROOT_DIR=%%~fI"

REM Defines the Python virtual environment activation script.
set VENV_ACTIVATION_SCRIPT_FILE=%PROJECT_ROOT_DIR%\venv\Scripts\activate

REM Navigate to the project root directory.
echo Navigating to project root directory '%PROJECT_ROOT_DIR%'
pushd "%PROJECT_ROOT_DIR%" || (
    echo "Error: failed to navigate to '%PROJECT_ROOT_DIR%'"
    exit /b 1
)

REM Checks if virtual environment activation script exists.
echo Checking if if virtual environment activation script exists at '%VENV_ACTIVATION_SCRIPT_FILE%'
if exist "%VENV_ACTIVATION_SCRIPT_FILE%" (
    echo Found activation script, activating virtual enviroment
    call "%VENV_ACTIVATION_SCRIPT_FILE%"
    if errorlevel 1 (
        echo Error: failed to run activation script at '%VENV_ACTIVATION_SCRIPT_FILE%'
        popd
        exit /b 1
    )
) else (
    echo "ERROR: Failed to find activation script '%VENV_ACTIVATION_SCRIPT_FILE%'"
)

REM Restore the original working directory.
echo Restoring the original working directory.
popd
