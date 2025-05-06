# PowerShell script to install the package in development mode and run the example

# Create virtual environment if it doesn't exist
if (-not (Test-Path .venv)) {
    Write-Host "Creating virtual environment..."
    uv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
uv pip install -r requirements.txt

# Install the package in development mode
Write-Host "Installing package in development mode..."
uv pip install -e .

# Run the example
Write-Host "Running example..."
python examples/parse_twincat_files.py
