
REM Specifies the directory where the QuickJS build files will be stored
BUILD_DIR="qjs_build"

REM ADD CODE HERE to install clang and make using winget

REM Displays the installed version of the Clang compiler.
REM Clang is the compiler used to compile the QuickJS source code.
REM This command helps verify that the compiler is available.
clang --version

REM Displays the installed version of GNU Make.
REM Make is a build automation tool that reads instructions from a Makefile
REM and executes the commands required to compile the QuickJS project.
make --version

REM Creates the directory specified by BUILD_DIR.
REM This directory will be used to store the downloaded QuickJS source files
REM and related build resources.
mkdir "$BUILD_DIR"

REM Changes the current working directory to the directory named BUILD_DIR.
REM This allows subsequent commands to execute within the build directory.
REM NOTE: The variable should be referenced as "$BUILD_DIR".
cd "$BUILD_DIR"

REM Downloads the official QuickJS source-code archive from Bellard's website.
REM The -L option follows HTTP redirects if the download URL redirects.
REM The -O option saves the downloaded file using its original filename.
REM The archive contains the QuickJS source code and build instructions.
curl -LO https://bellard.org/quickjs/quickjs-2025-04-26.tar.xz

REM Extracts the contents of the downloaded .tar.xz archive.
REM The x option extracts files.
REM The f option specifies the archive filename.
REM The extracted files are placed in a directory named quickjs-2025-04-26.
tar xf quickjs-2025-04-26.tar.xz

REM Changes the current working directory to the extracted QuickJS source directory.
REM This is necessary because the Makefile required to compile QuickJS
REM is located inside this directory.
cd quickjs-2025-04-26

REM Removes previously compiled files and temporary build artifacts.
REM This ensures that the next compilation starts with a clean build environment.
make clean

REM Executes the newly compiled QuickJS interpreter.
REM The -e option instructs QuickJS to execute the supplied JavaScript code.
REM The JavaScript console.log() function prints the specified message.
REM This acts as a basic test to verify that QuickJS compiled successfully
REM and that the interpreter can execute JavaScript code.
./qjs -e 'console.log("QuickJS is working!")'
