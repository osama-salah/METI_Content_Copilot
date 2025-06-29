#!/bin/bash
set -e

PYTHON_MAJOR_VERSION=$(python -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR_VERSION=$(python -c 'import sys; print(sys.version_info[1])')

# 3.11.3 is confirmed stable to build
if [ $PYTHON_MAJOR_VERSION == 3 ]
then
    if [ -d .venv ]; then
        echo "Virtual environment already exists"
    else
        echo "Creating virtual environment"
        python -m venv .venv
    fi
    system=$(uname -s)

    if [ -f .venv/Scripts/activate ]; then
        source .venv/Scripts/activate
    elif [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
    else
        echo "Error: Could not find activation script in .venv/Scripts/activate or .venv/bin/activate"
        exit 1
    fi

    python --version
    
 
    echo "Installing dependencies"
    pip install -r requirements.txt
    echo "Virtual environment setup complete"

else
    echo "Python version is not supported:$PYTHON_MAJOR_VERSION.$PYTHON_MINOR_VERSION.x"
    exit 1
fi
