
@echo off
setlocal

REM Initialize project directories
call "%~dp0PROJECT_ROOT_DIR.bat"
call "%~dp0PROJECT_WINDOWS_BIN_DIR.bat"

REM Define download URLs
set "GITHUB_YT_DLP_FFMPEG_BUILDS_LATEST_RELEASE_URL=https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest"
set "DOWNLOAD_URLS[0]=%GITHUB_YT_DLP_FFMPEG_BUILDS_LATEST_RELEASE_URL%/ffmpeg-master-latest-win32-gpl.zip"
set "DOWNLOAD_URLS[1]=%GITHUB_YT_DLP_FFMPEG_BUILDS_LATEST_RELEASE_URL%/ffmpeg-master-latest-win64-gpl.zip"
set "DOWNLOAD_URLS[2]=%GITHUB_YT_DLP_FFMPEG_BUILDS_LATEST_RELEASE_URL%/ffmpeg-master-latest-winarm64-gpl.zip"

REM Define output directories, temporary directories and executable locations
set "OUTPUT_FILE=%PROJECT_WINDOWS_BIN_DIR%\ffmpeg.zip"
set "EXTRACT_DIR=%PROJECT_WINDOWS_BIN_DIR%\ffmpeg_temp"
set "FFMPEG_PATH=%PROJECT_WINDOWS_BIN_DIR%\ffmpeg.exe"
set "FFPROBE_PATH=%PROJECT_WINDOWS_BIN_DIR%\ffprobe.exe"

REM Detect native Windows architecture
echo.
echo Checking processor architecture...
if defined PROCESSOR_ARCHITEW6432 (
    set "FOUND_PROCESSOR_ARCHITECTURE=%PROCESSOR_ARCHITEW6432%"
) else (
    set "FOUND_PROCESSOR_ARCHITECTURE=%PROCESSOR_ARCHITECTURE%"
)
echo Successfully found Windows architecture: %FOUND_PROCESSOR_ARCHITECTURE%

REM Select the appropriate FFmpeg build
echo.
echo Selecting appropriate FFmpeg build...
if /i "%FOUND_PROCESSOR_ARCHITECTURE%"=="x86" (
    set "DOWNLOAD_URL=%DOWNLOAD_URLS[0]%"
) else if /i "%FOUND_PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "DOWNLOAD_URL=%DOWNLOAD_URLS[1]%"
) else if /i "%FOUND_PROCESSOR_ARCHITECTURE%"=="ARM64" (
    set "DOWNLOAD_URL=%DOWNLOAD_URLS[2]%"
) else (
    echo Error: Unsupported Windows architecture '%FOUND_PROCESSOR_ARCHITECTURE%'
    exit /b 1
)
echo Successfully selected download url '%DOWNLOAD_URL%'

REM Create Windows binary directory
echo.
echo Creating Windows binary directory at '%PROJECT_WINDOWS_BIN_DIR%'...
if not exist "%PROJECT_WINDOWS_BIN_DIR%" (
    mkdir "%PROJECT_WINDOWS_BIN_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create Windows binary directory.
        exit /b 1
    )
)
echo Successfully created Windows binary directory

REM Download FFmpeg
echo.
echo Downloading FFmpeg...
echo Source: %DOWNLOAD_URL%
echo Destination: %OUTPUT_FILE%
curl.exe --location --fail --output "%OUTPUT_FILE%" "%DOWNLOAD_URL%"
if errorlevel 1 (
    echo Error: Failed to download FFmpeg.
    goto :cleanup_failure
)
echo FFmpeg downloaded successfully

REM Remove old extraction directory
echo.
echo Removing old extraction directory '%EXTRACT_DIR%'...
if exist "%EXTRACT_DIR%" (
    rmdir /s /q "%EXTRACT_DIR%"
    if exist "%EXTRACT_DIR%" (
        echo Error: Failed to remove old extraction directory.
        goto :cleanup_failure
    )
)
echo Successfully removed old extraction directory.

REM Create new extraction directory
echo.
echo Creating new extraction directory at '%EXTRACT_DIR%'...
mkdir "%EXTRACT_DIR%"
if errorlevel 1 (
    echo Error: Failed to create extraction directory.
    goto :cleanup_failure
)
echo Successfully created new extraction directory.

REM Extract the downloaded ZIP archive
echo.
echo Extracting FFmpeg archive...
echo from '%OUTPUT_FILE%'
echo to '%EXTRACT_DIR%'
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%OUTPUT_FILE%' -DestinationPath '%EXTRACT_DIR%' -Force"
if errorlevel 1 (
    echo Error: Failed to extract FFmpeg archive
    echo from '%OUTPUT_FILE%'
    echo to '%EXTRACT_DIR%'
    goto :cleanup_failure
)
echo Successfully extracted FFmpeg archive

REM Find and install ffmpeg
echo.
echo Locating ffmpeg executable within '%EXTRACT_DIR%'...
for /r "%EXTRACT_DIR%" %%F in (*ffmpeg.exe) do (
    if /i "%%~nxF"=="ffmpeg.exe" (
        if exist "%%F" (
            if not exist "%FFMPEG_PATH%" (
                echo     Found ffmpeg.exe at '%%F'
                echo     Copying '%%F' to '%FFMPEG_PATH%'...
                copy /y "%%F" "%FFMPEG_PATH%"
                if errorlevel 1 (
                    echo     Error: Failed to copy ffmpeg.exe.
                    goto :cleanup_failure
                )
            )
        )
    )
)

REM Verify extracted ffmpeg executable
if not exist "%FFMPEG_PATH%" (
    echo Error: ffmpeg.exe did not successfully install at '%FFMPEG_PATH%'
    goto :cleanup_failure
)

REM Find and install ffprobe
echo.
echo Locating ffprobe executable within '%EXTRACT_DIR%'...
for /r "%EXTRACT_DIR%" %%F in (*ffprobe.exe) do (
    if /i "%%~nxF"=="ffprobe.exe" (
        if exist "%%F" (
            if not exist "%FFPROBE_PATH%" (
                echo     Found ffprobe.exe at '%%F'
                echo     Copying '%%F' to '%FFPROBE_PATH%'...
                copy /y "%%F" "%FFPROBE_PATH%"
                if errorlevel 1 (
                    echo     Error: Failed to copy ffprobe.exe.
                    goto :cleanup_failure
                )
            )
        )
    )
)

REM Verify extracted ffprobe executable
if not exist "%FFPROBE_PATH%" (
    echo Error: ffprobe.exe did not successfully install at '%FFPROBE_PATH%'
    goto :cleanup_failure
)

REM Test FFmpeg executable
"%FFMPEG_PATH%" -version >nul 2>&1
if errorlevel 1 (
    echo Error: ffmpeg.exe failed its execution test.
    goto :cleanup_failure
)

REM Test FFprobe executable
"%FFPROBE_PATH%" -version >nul 2>&1
if errorlevel 1 (
    echo Error: ffprobe.exe failed its execution test.
    goto :cleanup_failure
)

REM Clean up temporary files
echo.
echo Cleaning up temporary files...
echo Deleting downloaded FFmpeg zip at '%OUTPUT_FILE%'
del /q "%OUTPUT_FILE%"
echo Removing extraction directory at '%EXTRACT_DIR%'
rmdir /s /q "%EXTRACT_DIR%"

REM Installation completed
echo.
echo FFmpeg installed successfully!
echo.
echo Architecture: %FOUND_PROCESSOR_ARCHITECTURE%
echo FFmpeg:       %PROJECT_WINDOWS_BIN_DIR%\ffmpeg.exe
echo FFprobe:      %PROJECT_WINDOWS_BIN_DIR%\ffprobe.exe
endlocal
exit /b 0

REM Failure cleanup
:cleanup_failure
echo.
echo Installation failed. Cleaning up temporary files...
if exist "%OUTPUT_FILE%" del /q "%OUTPUT_FILE%"
if exist "%EXTRACT_DIR%" rmdir /s /q "%EXTRACT_DIR%"
endlocal
exit /b 1
