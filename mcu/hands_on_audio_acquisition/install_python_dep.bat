@echo off
setlocal

:: Detect the operating system
if "%OS%"=="Windows_NT" (
    goto :windows
) else (
    goto :unix
)

:windows
:: Function to detect Python executable
for %%i in (python python3) do (
    where %%i >nul 2>nul
    if not errorlevel 1 (
        set PYTHON_EXEC=%%i
        goto :found_python
    )
)
echo Python is not installed.
exit /b 1

:found_python
:: Install required Python packages
%PYTHON_EXEC% -m pip install argparse numpy pyserial soundfile plotly

:: Print the command to launch the program
echo To launch the program, run:
echo %PYTHON_EXEC% uart-reader_V3.py
exit /b 0

:unix
#!/bin/bash

# Function to detect Python executable
detect_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_EXEC=python3
    elif command -v python &>/dev/null; then
        PYTHON_EXEC=python
    else
        echo "Python is not installed."
        exit 1
    fi
}

# Function to install packages
install_packages() {
    $PYTHON_EXEC -m pip install argparse numpy pyserial soundfile plotly
}

# Function to print the command to launch the program
print_launch_command() {
    echo "To launch the program, run:"
    echo "$PYTHON_EXEC uart-reader_V3.py"
}

# Main script logic
detect_python
install_packages
print_launch_command
exit 0