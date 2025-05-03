# PowerShell script to set up uv environment and install dependencies

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

Write-Host "Setup complete! You can now use the virtual environment."
