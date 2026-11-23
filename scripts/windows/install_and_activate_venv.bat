
@echo off

REM Define project directories and file paths
call "%~dp0PROJECT_ROOT_DIR.bat"
if not defined PROJECT_ROOT_DIR (
    echo ERROR: Failed to define project root directory.
    exit /b 1
)
set "PYTHON3_VENV_REQUIREMENTS_TXT_PATH=%PROJECT_ROOT_DIR%\requirements.txt"
set "PYTHON3_VENV_DIR=%PROJECT_ROOT_DIR%\venv"
set "VENV_ACTIVATION_SCRIPT_FILE=%PYTHON3_VENV_DIR%\Scripts\activate"

REM Navigate to the project root directory.
echo.
echo Navigating to the project root directory '%PROJECT_ROOT_DIR%'...
pushd "%PROJECT_ROOT_DIR%" || (
    echo Error: failed to navigate to the project root directory.
    exit /b 1
)
echo Successfully navigated to the project root directory.

REM Check if python3 exists
echo.
echo Checking if python3 is available in PATH...
python3 --version
if errorlevel 1 (
    echo ERROR: python3 is unavailable in PATH.
    goto :ERROR
)
echo Successfully checked if python3 is available in PATH.

REM Check if venv is installed in python3
echo.
echo Checking if python3 venv is available...
python3 -m venv --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: python3 venv is unavailable.
    goto :ERROR
)
echo Successfully checked if python3 venv is available.

REM Checking if requirements.txt exists
echo.
echo Checking if requirements.txt exists at '%PYTHON3_VENV_REQUIREMENTS_TXT_PATH%'...
if not exist "%PYTHON3_VENV_REQUIREMENTS_TXT_PATH%" (
    echo ERROR: requirements.txt does not exist.
    goto :ERROR
)
echo Successfully checked if requirements.txt exists.

REM Create python3 virtual environment
echo.
echo Creating python3 virtual environment at '%PYTHON3_VENV_DIR%'...
if not exist "%PYTHON3_VENV_DIR%" (
    python3 -m venv "%PYTHON3_VENV_DIR%"
)
if errorlevel 1 (
    echo ERROR: failed to create python3 virtual environment.
    goto :ERROR
)
echo Successfully created python3 virtual environment.

REM Activate virtual enviroment
echo.
echo Activating virtual enviroment at '%PYTHON3_VENV_DIR%'...
echo Checking if if virtual environment activation script exists at '%VENV_ACTIVATION_SCRIPT_FILE%'.
if exist "%VENV_ACTIVATION_SCRIPT_FILE%" (
    echo Found activation script, activating virtual enviroment.
    call "%VENV_ACTIVATION_SCRIPT_FILE%"
    if errorlevel 1 (
        echo Error: failed to run activation script.
        goto :ERROR
    )
) else (
    echo ERROR: Failed to find activation script.
    goto :ERROR
)
echo Successfully activated virtual enviroment.

REM Check if python3 pip is installed
echo.
echo Checking if python3 pip is installed...
python3 -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: python3 pip is not installed.
    goto :ERROR
)
echo Successfully checked if python3 pip is installed.

REM Install required python3 packages into venv listed in requirements.txt
echo.
echo Installing required python3 packages into venv listed in '%PYTHON3_VENV_REQUIREMENTS_TXT_PATH%'...
python3 -m pip install --requirement "%PYTHON3_VENV_REQUIREMENTS_TXT_PATH%" >nul 2>&1
if errorlevel 1 (
    echo ERROR: failed to install required python3 packages into venv.
    goto :ERROR
)
echo Successfully installed required python3 packages into venv.

REM Success
echo.
echo Successfully installed and activated python3 venv.
echo Virtual environment: '%PYTHON3_VENV_DIR%'.
echo Requirements file:   '%PYTHON3_VENV_REQUIREMENTS_TXT_PATH%'.
goto :END

REM Erorr handling
:ERROR
echo.
echo ERROR: python3 virtual environment setup failed.
set "EXIT_CODE=1"
goto :CLEANUP

REM cleanup
:END
set "EXIT_CODE=0"

:CLEANUP

REM Deactivate virtual environment if setup failed and it is activated.
echo.
echo Checking whether virtual environment deactivation is required...
if not "%EXIT_CODE%"=="0" (
    if defined VIRTUAL_ENV (
        echo Deactivating virtual environment due to setup failure.
        call deactivate
        if errorlevel 1 (
            echo WARNING: Failed to deactivate virtual environment.
        ) else (
            echo Successfully deactivated virtual environment.
        )
    ) else (
        echo Skipping deactivation because virtual environment is not activated.
    )
) else (
    echo Skipping deactivation because setup was successful.
)

REM Restore the original working directory saved by pushd.
echo.
echo Restoring the original working directory...
popd
if errorlevel 1 (
    echo ERROR: Failed to restore the original working directory.
    set "EXIT_CODE=1"
)
echo Successfully restored the original working directory.

exit /b %EXIT_CODE%
