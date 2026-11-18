
#!/bin/bash

# Specifies the directory where the QuickJS build files will be stored
BUILD_DIR="qjs_build"

# Checks whether the Xcode Command Line Tools are installed on macOS.
# If they are not installed, macOS will prompt the user to install them.
# These tools provide essential development utilities, including compilers.
xcode-select --install

# Displays the installed version of the Clang compiler.
# Clang is the compiler used to compile the QuickJS source code.
# This command helps verify that the compiler is available.
clang --version

# Displays the installed version of GNU Make.
# Make is a build automation tool that reads instructions from a Makefile
# and executes the commands required to compile the QuickJS project.
make --version

# Creates the directory specified by BUILD_DIR.
# This directory will be used to store the downloaded QuickJS source files
# and related build resources.
mkdir "$BUILD_DIR"

# Changes the current working directory to the directory named BUILD_DIR.
# This allows subsequent commands to execute within the build directory.
# NOTE: The variable should be referenced as "$BUILD_DIR".
cd "$BUILD_DIR"

# Downloads the official QuickJS source-code archive from Bellard's website.
# The -L option follows HTTP redirects if the download URL redirects.
# The -O option saves the downloaded file using its original filename.
# The archive contains the QuickJS source code and build instructions.
curl -LO https://bellard.org/quickjs/quickjs-2025-04-26.tar.xz

# Extracts the contents of the downloaded .tar.xz archive.
# The x option extracts files.
# The f option specifies the archive filename.
# The extracted files are placed in a directory named quickjs-2025-04-26.
tar xf quickjs-2025-04-26.tar.xz

# Changes the current working directory to the extracted QuickJS source directory.
# This is necessary because the Makefile required to compile QuickJS
# is located inside this directory.
cd quickjs-2025-04-26

# Removes previously compiled files and temporary build artifacts.
# This ensures that the next compilation starts with a clean build environment.
make clean

# Executes the newly compiled QuickJS interpreter.
# The -e option instructs QuickJS to execute the supplied JavaScript code.
# The JavaScript console.log() function prints the specified message.
# This acts as a basic test to verify that QuickJS compiled successfully
# and that the interpreter can execute JavaScript code.
./qjs -e 'console.log("QuickJS is working!")'

