
@echo off

REM Defines the absolute, normalized path to the project root directory.
for %%I in ("%~dp0..\..") do set "PROJECT_ROOT_DIR=%%~fI"

REM Navigate to the project root directory.
echo ""
pushd "%PROJECT_ROOT_DIR%" || (
    echo "Error: failed to navigate to '%PROJECT_ROOT_DIR%'"
    exit /b 1
)

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

REM Defines the directory where the compiled QuickJS executable will be stored.
set "BIN_DIR=%PROJECT_ROOT_DIR%\bin\windows"

REM Check whether MSYS2 is already installed.
REM If it is not installed, WinGet will install it.
echo Checking if MSYS2 is installed...
if not exist "%MSYS2_BASH%" (

    REM Check whether Windows Package Manager (WinGet) is available.
    echo Checking if winget is installed...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo ERROR: WinGet is not installed or unavailable.
        popd
        exit /b 1
    )

    REM Install MSYS2.
    REM MSYS2 provides the compiler, build tools and Unix command-line utilities.
    echo Installing MSYS2...
    winget install --id MSYS2.MSYS2 --exact --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo ERROR: MSYS2 installation failed.
        popd
        exit /b 1
    )
)


REM Verify that MSYS2 was installed in the expected directory.
echo Checking that MSYS2 is installed...
if not exist "%MSYS2_BASH%" (
    echo ERROR: MSYS2 Bash executable was not found.
    popd
    exit /b 1
)

REM Update the MSYS2 package databases and installed packages.
REM The first update may update MSYS2 itself and its core packages.
echo Updating MSYS2 packages...
"%MSYS2_BASH%" -lc "pacman -Syu --noconfirm"
if errorlevel 1 (
    echo ERROR: Initial MSYS2 update failed.
    popd
    exit /b 1
)

REM Complete any remaining package updates.
REM MSYS2 may require a second update after updating its core packages.
echo Completing MSYS2 updates...
"%MSYS2_BASH%" -lc "pacman -Su --noconfirm"
if errorlevel 1 (
    echo ERROR: Final MSYS2 update failed.
    popd
    exit /b 1
)

REM Install the MinGW-w64 GCC compiler and GNU Make.
REM GCC compiles QuickJS, while GNU Make processes its Makefile.
REM MSYS2 also provides Unix utilities such as uname, cat and rm.
echo Installing MinGW-w64 GCC and GNU Make...
"%MSYS2_BASH%" -lc "pacman -S --needed --noconfirm mingw-w64-x86_64-gcc make"
if errorlevel 1 (
    echo ERROR: Failed to install MinGW-w64 GCC and GNU Make.
    popd
    exit /b 1
)

REM Display the installed GCC version.
REM This verifies that the compiler is accessible in the MINGW64 environment.
echo Checking that GCC is installed...
"%MSYS2_BASH%" -lc "gcc --version"
if errorlevel 1 (
    echo ERROR: GCC is unavailable.
    popd
    exit /b 1
)

REM Display the installed GNU Make version.
REM This verifies that the build automation tool is accessible.
echo Checking that GNU Make is installed...
"%MSYS2_BASH%" -lc "make --version"
if errorlevel 1 (
    echo ERROR: GNU Make is unavailable.
    popd
    exit /b 1
)

REM Create the build directory if it does not already exist.
echo Creating QuickJS build directory...
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create QuickJS build directory.
    popd
    exit /b 1
)

REM Navigate into the QuickJS build directory.
echo Navigating into the QuickJS build directory '%BUILD_DIR%'...
cd /d "%BUILD_DIR%" || (
    echo ERROR: Unable to access build directory.
    popd
    exit /b 1
)

REM Check whether the QuickJS source archive already exists.
REM If not, downloads it.
if exist "%QJS_TAR_SOURCE_FILE_NAME%" (
    echo QuickJS source archive already exists. Skipping download.
) else (
    REM Download the official QuickJS source archive.
    REM -L follows HTTP redirects.
    REM -O saves the archive using its original filename.
    echo Downloading QuickJS source code...
    curl -fL -O "%QJS_TAR_SOURCE_URL%"
    if errorlevel 1 (
        echo ERROR: Failed to download QuickJS source code.
        popd
        exit /b 1
    )
)

REM Extract the downloaded XZ-compressed TAR archive.
REM The extracted source files are placed in the directory specified by QJS_SOURCE_DIR.
echo Extracting QuickJS source code...
tar xf "%QJS_TAR_SOURCE_FILE_NAME%"
if errorlevel 1 (
    echo ERROR: Failed to extract QuickJS source code.
    popd
    exit /b 1
)

REM Navigate into the extracted QuickJS source directory and compile it.
REM The build is executed inside the MINGW64 environment.
REM make clean removes previously generated build artifacts.
REM CC=gcc tells QuickJS to use the MinGW-w64 GCC compiler.
echo Cleaning previous QuickJS build artifacts...
"%MSYS2_BASH%" -lc "cd '%QJS_SOURCE_DIR%' && make clean"
if errorlevel 1 (
    echo ERROR: Failed to clean previous QuickJS build artifacts.
    popd
    exit /b 1
)

REM Compile QuickJS using MinGW-w64 GCC.
echo Compiling QuickJS...
"%MSYS2_BASH%" -lc "cd '%QJS_SOURCE_DIR%' && make CONFIG_WIN32=y CROSS_PREFIX= CC=gcc LDFLAGS=-static qjs.exe"
if errorlevel 1 (
    echo ERROR: QuickJS compilation failed.
    popd
    exit /b 1
)

REM Execute the compiled QuickJS interpreter directly from Windows.
REM The --eval option executes the supplied JavaScript expression.
REM This verifies that the compiled interpreter can execute JavaScript.
echo Testing QuickJS...
"%QJS_SOURCE_DIR%\qjs.exe" --eval "console.log('QuickJS is working!')"
if errorlevel 1 (
    echo ERROR: QuickJS runtime verification failed.
    popd
    exit /b 1
)

REM Create the output directory if it does not already exist.
echo Creating Windows binary directory...
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to create Windows binary directory.
    popd
    exit /b 1
)

REM Copy the compiled QuickJS executable into the Windows binary directory.
echo "Copying QuickJS executable from '%QJS_SOURCE_DIR%\qjs.exe' to '%BIN_DIR%\qjs.exe'..."
copy /Y "%QJS_SOURCE_DIR%\qjs.exe" "%BIN_DIR%\qjs.exe" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy QuickJS executable.
    popd
    exit /b 1
)

REM Restore the original working directory saved by pushd.
popd

echo.
echo QuickJS setup completed successfully.
