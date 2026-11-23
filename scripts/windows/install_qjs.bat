
@echo off

REM Initialize project directories
call "%~dp0PROJECT_ROOT_DIR.bat"
if not defined PROJECT_ROOT_DIR (
    echo ERROR: Failed to define project root directory.
    exit /b 1
)
call "%~dp0PROJECT_WINDOWS_BIN_DIR.bat"
if not defined PROJECT_WINDOWS_BIN_DIR (
    echo ERROR: Failed to define project windows binary directory.
    exit /b 1
)

REM Navigate to the project root directory.
echo.
echo Navigating to the project root directory '%PROJECT_ROOT_DIR%'...
pushd "%PROJECT_ROOT_DIR%" || (
    echo Error: failed to navigate to the project root directory.
    exit /b 1
)
echo Successfully navigated to the project root directory.

REM Defines the directory used to store QuickJS build resources.
REM This directory will contain the downloaded source archive
REM and the extracted QuickJS source code.
set "BUILD_DIR=%PROJECT_ROOT_DIR%\qjs_build"

REM Defines the supported QuickJS source versions.
set "SUPPORTED_QJS_VERSIONS[0]=quickjs-2026-06-04"
set "SUPPORTED_QJS_VERSIONS[1]=quickjs-2025-09-13"
set "SUPPORTED_QJS_VERSIONS[2]=quickjs-2025-04-26"
set "SUPPORTED_QJS_VERSIONS[3]=quickjs-2024-01-13"
set "SUPPORTED_QJS_VERSIONS[4]=quickjs-2023-12-09"
set "SUPPORTED_QJS_VERSIONS[5]=quickjs-2021-03-27"
set "SUPPORTED_QJS_VERSIONS[6]=quickjs-2020-11-08"

REM Specifies the QuickJS source version to download and compile.
set "QJS_VERSION=%SUPPORTED_QJS_VERSIONS[0]%"

REM Specifies the filename of the downloaded QuickJS source archive.
set "QJS_TAR_SOURCE_FILE_NAME=%QJS_VERSION%.tar.xz"

REM Defines the official QuickJS source archive URL.
set "QJS_TAR_SOURCE_URL=https://bellard.org/quickjs/%QJS_TAR_SOURCE_FILE_NAME%"

REM Defines the directory containing the extracted QuickJS source code.
set "QJS_SOURCE_DIR=%BUILD_DIR%\%QJS_VERSION%"

REM Defines the 
set "QJS_OUTPUT_EXECUTABLE_PATH=%QJS_SOURCE_DIR%\qjs.exe"

REM Defines the MSYS2 installation directory.
REM This is the default installation directory used by the MSYS2 installer.
set "MSYS2_ROOT=C:\msys64"

REM Defines the MSYS2 Bash executable.
set "MSYS2_BASH=%MSYS2_ROOT%\usr\bin\bash.exe"

REM Specifies the MSYS2 environment to use.
REM MINGW64 provides the 64-bit MinGW-w64 GCC toolchain.
set "MSYSTEM=MINGW64"

REM Prevents MSYS2 Bash from changing the current working directory.
set "CHERE_INVOKING=1"

REM Install MSYS2
echo.
echo Installing MSYS2 at '%MSYS2_ROOT%'...
if not exist "%MSYS2_BASH%" (

    REM Check whether Windows Package Manager (WinGet) is available.
    echo.
    echo MSYS2 is not installed, installing using winget.
    echo Checking if winget is installed.
    where winget >nul 2>&1
    if errorlevel 1 (
        echo ERROR: WinGet is not installed or unavailable.
        echo Opening Microsoft Store to install WinGet
        start "" "ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1"
        popd
        exit /b 1
    )
    echo Successfully checked that winget is installed.

    REM Install MSYS2.
    REM MSYS2 provides the compiler, build tools and Unix command-line utilities.
    echo Installing MSYS2...
    winget install --id MSYS2.MSYS2 --exact --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo ERROR: MSYS2 installation failed.
        popd
        exit /b 1
    )
    echo Successfully installed MSYS2 using winget.

) else (
    echo MSYS2 is already installed.
)
echo Successfully installed MSYS2.

REM Update the MSYS2 package databases and installed packages.
REM The 1st update may update MSYS2 itself and its core packages.
echo.
echo Updating MSYS2 packages...
"%MSYS2_BASH%" -lc "pacman -Syu --noconfirm"
if errorlevel 1 (
    echo ERROR: Initial MSYS2 update failed.
    popd
    exit /b 1
)
echo Successfully updated MSYS2.

REM Complete any remaining package updates.
REM MSYS2 may require a 2nd update after updating its core packages.
echo.
echo Completing MSYS2 updates...
"%MSYS2_BASH%" -lc "pacman -Su --noconfirm"
if errorlevel 1 (
    echo ERROR: Final MSYS2 update failed.
    popd
    exit /b 1
)
echo Successfully completed MSYS2 updates.

REM Install the MinGW-w64 GCC compiler and GNU Make.
REM GCC compiles QuickJS, while GNU Make processes its Makefile.
REM MSYS2 also provides Unix utilities such as uname, cat and rm.
echo.
echo Installing MinGW-w64 GCC and GNU Make...
"%MSYS2_BASH%" -lc "pacman -S --needed --noconfirm mingw-w64-x86_64-gcc make"
if errorlevel 1 (
    echo ERROR: Failed to install MinGW-w64 GCC and GNU Make.
    popd
    exit /b 1
)
echo Successfully installed MinGW-w64 GCC and GNU Make.

REM Display the installed GCC version.
REM This verifies that the compiler is accessible in the MINGW64 environment.
echo.
echo Checking that GCC is installed...
"%MSYS2_BASH%" -lc "gcc --version"
if errorlevel 1 (
    echo ERROR: GCC is unavailable.
    popd
    exit /b 1
)
echo Successfully checked that GCC is installed.

REM Display the installed GNU Make version.
REM This verifies that the build automation tool is accessible.
echo.
echo Checking that GNU Make is installed...
"%MSYS2_BASH%" -lc "make --version"
if errorlevel 1 (
    echo ERROR: GNU Make is unavailable.
    popd
    exit /b 1
)
echo Successfully checked that GNU Make is installed.

REM Create the build directory if it does not already exist.
echo.
echo Creating QuickJS build directory at '%BUILD_DIR%'...
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create QuickJS build directory.
    popd
    exit /b 1
)
echo Successfully created QuickJS build directory.

REM Navigate into the QuickJS build directory.
echo.
echo Navigating into the QuickJS build directory '%BUILD_DIR%'...
cd /d "%BUILD_DIR%" || (
    echo ERROR: Unable to access build directory.
    popd
    exit /b 1
)
echo Successfully navigated into the QuickJS build directory.

REM Download the official QuickJS source archive.
REM -L follows HTTP redirects.
REM -O saves the archive using its original filename.
echo.
echo Downloading QuickJS source archive...
echo from '%QJS_TAR_SOURCE_URL%'
echo to '%QJS_TAR_SOURCE_FILE_NAME%'
curl -fL -O "%QJS_TAR_SOURCE_URL%"
if errorlevel 1 (
    echo ERROR: Failed to download QuickJS source code.
    popd
    exit /b 1
)
echo Successfully downloaded QuickJS source archive.

REM Extract the downloaded XZ-compressed TAR archive.
REM The archive contains its own version directory, which is extracted into BUILD_DIR.
echo.
echo Extracting QuickJS source code...
echo from '%QJS_TAR_SOURCE_FILE_NAME%'
echo to '%BUILD_DIR%'
tar -xf "%QJS_TAR_SOURCE_FILE_NAME%" -C "%BUILD_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to extract QuickJS source code.
    popd
    exit /b 1
)
echo Successfully extracted QuickJS source code.

REM Navigate into the extracted QuickJS source directory and compile it.
REM The build is executed inside the MINGW64 environment.
REM make clean removes previously generated build artifacts.
REM CC=gcc tells QuickJS to use the MinGW-w64 GCC compiler.
echo.
echo Cleaning previous QuickJS build artifacts at '%QJS_SOURCE_DIR%'...
"%MSYS2_BASH%" -lc "cd '%QJS_SOURCE_DIR%' && make clean"
if errorlevel 1 (
    echo ERROR: Failed to clean previous QuickJS build artifacts.
    popd
    exit /b 1
)
echo Successfully cleaned previous QuickJS build artifacts.

REM Compile QuickJS using MinGW-w64 GCC.
echo.
echo Compiling QuickJS at '%QJS_SOURCE_DIR%'...
"%MSYS2_BASH%" -lc "cd '%QJS_SOURCE_DIR%' && make CONFIG_WIN32=y CROSS_PREFIX= CC=gcc LDFLAGS=-static qjs.exe"
if errorlevel 1 (
    echo ERROR: QuickJS compilation failed.
    popd
    exit /b 1
)
echo Successfully compiled QuickJS.

REM Execute the compiled QuickJS interpreter directly from Windows.
REM The --eval option executes the supplied JavaScript expression.
REM This verifies that the compiled interpreter can execute JavaScript.
echo.
echo Testing output QuickJS executable at '%QJS_OUTPUT_EXECUTABLE_PATH%'...
"%QJS_OUTPUT_EXECUTABLE_PATH%" --eval "console.log('QuickJS is working!')"
if errorlevel 1 (
    echo ERROR: QuickJS runtime verification failed.
    popd
    exit /b 1
)
echo Successfully tested output QuickJS executable.

REM Create the output directory if it does not already exist.
echo.
echo Creating Windows binary directory at '%PROJECT_WINDOWS_BIN_DIR%'...
if not exist "%PROJECT_WINDOWS_BIN_DIR%" mkdir "%PROJECT_WINDOWS_BIN_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create Windows binary directory.
    popd
    exit /b 1
)
echo Succesfully created Windows binary directory.

REM Copy the compiled QuickJS executable into the Windows binary directory.
echo.
echo Copying QuickJS executable...
echo from '%QJS_SOURCE_DIR%\qjs.exe'
echo to '%PROJECT_WINDOWS_BIN_DIR%\qjs.exe'
copy /Y "%QJS_OUTPUT_EXECUTABLE_PATH%" "%PROJECT_WINDOWS_BIN_DIR%\qjs.exe" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy QuickJS executable.
    popd
    exit /b 1
)
echo Successfully copied QuickJS executable.

REM Restore the original working directory saved by pushd.
echo.
echo Restoring the original working directory...
popd
if errorlevel 1 (
    echo ERROR: Failed to restore the original working directory.
    exit /b 1
)
echo Succesfully restored the original working directory.

echo.
echo QuickJS installation completed successfully.
