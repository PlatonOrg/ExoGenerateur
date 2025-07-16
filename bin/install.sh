#!/bin/bash

# COLORS
# Reset
Color_Off=$'\e[0m' # Text Reset

# Regular Colors
Red=$'\e[0;31m'    # Red
Green=$'\e[0;32m'  # Green
Yellow=$'\e[0;33m' # Yellow
Purple=$'\e[0;35m' # Purple
Cyan=$'\e[0;36m'   # Cyan

# --- Configuration Variables ---
VENV_DIR="venv"             # Name of the virtual environment directory
REQUIREMENTS_FILE="requirements.txt" # Name of the dependencies file
ENV_FILE=".env"             # Name of the file to store the API key
OUTPUT_DIR="output"         # Name of the output directory
LOCAL_FILE_DIR="local_file" # Name of the directory to store local file

# --- Utility Functions ---

# Function to find the most suitable Python executable
get_python_executable() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null; then
        echo "python"
    else
        echo "" # Returns empty if not found
    fi
}

# --- Initial Checks ---

# Checking for Python >= 3.7
PYTHON_CMD=$(get_python_executable)
if [ -z "$PYTHON_CMD" ]; then
    echo "Python:$Red ERROR - Python 3.7 (or newer) must be installed (see: https://www.python.org/).$Color_Off" >&2
    exit 1
fi

ver=$("$PYTHON_CMD" -c 'import sys; print("".join(map(str, sys.version_info[:2])))')
if [[ "$ver" -lt "37" ]]; then
    echo "Python:$Red ERROR - $("$PYTHON_CMD" -V | tr -d '\n') found, should be at least 3.7 (see: https://www.python.org/).$Color_Off" >&2
    exit 1
fi
echo "Python:$Green OK !$Color_Off"

# Checking if pip is installed
if ! "$PYTHON_CMD" -m pip --version &>/dev/null; then
    echo "pip:$Red ERROR - Pip must be installed. If Python is installed, try 'python3 -m ensurepip' or see https://pip.pypa.io/en/stable/installation/.$Color_Off" >&2
    exit 1
fi
echo "pip:$Green OK !$Color_Off"

# --- Virtual Environment Creation and Activation ---

echo "$Yellow"
echo "Creating virtual environment '$VENV_DIR'..."
echo "$Color_Off"

if [ -d "$VENV_DIR" ]; then
    echo "$Yellow Warning: Virtual environment '$VENV_DIR' already exists. Deleting and recreating...$Color_Off"
    rm -rf "$VENV_DIR" || { echo "$Red Error: Unable to delete directory '$VENV_DIR'. Check permissions.$Color_Off"; exit 1; }
fi

if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
    echo "$Red Error: Failed to create virtual environment. Ensure the 'venv' module is available (e.g., 'sudo apt-get install python3-venv' on Debian/Ubuntu).$Color_Off" >&2
    exit 1
fi
echo "$Green Virtual environment created successfully.$Color_Off"

echo "$Yellow"
echo "Activating virtual environment..."
echo "$Color_Off"
# Sourcing activation for the current shell. This only works if executed with 'source ./setup.sh'
# or if the user is prompted to do it manually at the end.
# For purely scripted use, we'll use the full venv executables.
source "$VENV_DIR/bin/activate" || {
    echo "$Yellow Warning: Automatic activation failed. Please activate manually after installation with 'source $VENV_DIR/bin/activate'.$Color_Off"
}
echo "$Green Virtual environment activated (or ready for manual activation).$Color_Off"

# --- Installing Dependencies within the Venv ---

echo "$Yellow"
echo "Installing dependencies from '$REQUIREMENTS_FILE' into the virtual environment...$Color_Off"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "$Red Error: The file '$REQUIREMENTS_FILE' was not found. Please create it with your dependencies (e.g., google-generativeai, python-dotenv).$Color_Off" >&2
    exit 1
fi

# Use pip from the virtual environment
VENV_PIP="$VENV_DIR/bin/pip"
if [ ! -f "$VENV_PIP" ]; then
    # Windows case (Git Bash might still use /bin/pip, but for CMD/Powershell)
    VENV_PIP="$VENV_DIR/Scripts/pip.exe"
    if [ ! -f "$VENV_PIP" ]; then
        echo "$Red Error: Could not find 'pip' executable in the virtual environment.$Color_Off" >&2
        exit 1
    fi
fi

if ! "$VENV_PIP" install -r "$REQUIREMENTS_FILE"; then
    echo -n "$Red" >&2
    echo "Error: Dependency installation failed. Check your '$REQUIREMENTS_FILE' or your internet connection.$Color_Off" >&2
    exit 1
fi
echo "$Green Dependencies installed successfully.$Color_Off"

---
### create local directory

echo "$Cyan"
echo "Creating project directories '$OUTPUT_DIR' and '$LOCAL_FILE_DIR'..."
echo "$Color_Off"

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "$Green Directory '$OUTPUT_DIR' created.$Color_Off"
else
    echo "$Yellow Directory '$OUTPUT_DIR' already exists. Skipping creation.$Color_Off"
fi

# Create local_file directory if it doesn't exist
if [ ! -d "$LOCAL_FILE_DIR" ]; then
    mkdir -p "$LOCAL_FILE_DIR"
    echo "$Green Directory '$LOCAL_FILE_DIR' created.$Color_Off"
else
    echo "$Yellow Directory '$LOCAL_FILE_DIR' already exists. Skipping creation.$Color_Off"
fi

--- Requesting and Storing Gemini API Key ---

echo "$Purple"
echo -e "\n--- Gemini API Key Configuration ---$Color_Off"
echo "To get your Gemini API key, visit: https://ai.google.dev/aistudio"
read -p "Please enter your Gemini API key (leave empty to configure later): " API_KEY

if [ -z "$API_KEY" ]; then
echo "$Yellow Warning: No API key entered. You will need to manually configure it in '$ENV_FILE' before using the API.$Color_Off"
else
# Create or update the .env file
echo "GOOGLE_API_KEY="$API_KEY"" > "$ENV_FILE"
echo "$Green Gemini API key stored in '$ENV_FILE'.$Color_Off"
fi

--- Updating .gitignore ---

echo "$Cyan"
echo "Updating .gitignore file...$Color_Off"
GITIGNORE_FILE=".gitignore"

if [ ! -f "$GITIGNORE_FILE" ]; then
echo "$Cyan Creating '$GITIGNORE\_FILE' file...$Color\_Off"
echo -e "\# Python\\n\_\_pycache\_\_/\\n\*.pyc\\n\*.pyo\\n\*.pyd\\n.Python\\n$VENV\_DIR/\\nenv/\\n$ENV_FILE\n\n# IDE files\n.idea/\n.vscode/\n\n# OS generated files\n.DS_Store\nThumbs.db" > "$GITIGNORE_FILE"
echo "$Green '$GITIGNORE_FILE' created with standard exclusions including '$ENV_FILE' and '$VENV_DIR/'. $Color_Off"
elif ! grep -q "$ENV_FILE" "$GITIGNORE_FILE" || ! grep -q "$VENV_DIR/" "$GITIGNORE_FILE"; then
echo "$Cyan Adding '$ENV_FILE' and '$VENV_DIR/' to your existing .gitignore...$Color_Off"
# Add only if not already present
! grep -q "$ENV_FILE" "$GITIGNORE_FILE" && echo "$ENV_FILE" >> "$GITIGNORE_FILE"
! grep -q "$VENV_DIR/" "$GITIGNORE_FILE" && echo "$VENV_DIR/" >> "$GITIGNORE_FILE"
echo "$Green '$ENV_FILE' and '$VENV_DIR/' added to .gitignore.$Color_Off"
else
echo "$Green '$ENV_FILE' and '$VENV_DIR/' are already listed in .gitignore. Perfect! $Color_Off"
fi

echo -e "$Green\n--- Installation and configuration complete! ---$Color_Off"
echo -e "$Cyan\nTo start working, activate your virtual environment with:$Color_Off"
echo "  source $VENV_DIR/bin/activate"
echo -e "$Cyan Then, you can run your Python scripts, for example:$Color_Off"
echo "  python main.py"
echo -e "$Cyan Remember to deactivate the environment when you're done with 'deactivate'.$Color_Off"