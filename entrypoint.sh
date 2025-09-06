#!/bin/bash

# Define the target directory for Python packages
PYTHON_LIBS_DIR="/usr/src/app/site-packages"

# Check if requirements.txt exists


if [ -f "requirements.txt" ]; then
    echo "requirements.txt found. Checking Python dependencies..."

    # Check if the target directory for Python libs exists and contains packages
    if [ -d "${PYTHON_LIBS_DIR}" ] && [ "$(ls -A ${PYTHON_LIBS_DIR})" ]; then
        echo "Python packages already present in ${PYTHON_LIBS_DIR}. Skipping re-installation."
    else
        echo "Python packages not found or directory is empty. Installing..."
        # Upgrade pip to the latest version
        pip install --upgrade pip

        # Install dependencies from requirements.txt to the specified target directory
        pip install --target="${PYTHON_LIBS_DIR}" -r requirements.txt

        echo "Python dependencies installed."
    fi
else
    echo "requirements.txt not found. Skipping Python dependency check."
fi

# Export PYTHONPATH to include the site-packages directory where pip installs packages
export PYTHONPATH="${PYTHON_LIBS_DIR}":$PYTHONPATH

# Execute the command passed to the entrypoint
exec "$@"