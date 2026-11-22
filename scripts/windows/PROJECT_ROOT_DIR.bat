
@echo off

REM Defines the absolute, normalized path to the project root directory.
for %%I in ("%~dp0..\..") do set "PROJECT_ROOT_DIR=%%~fI"
