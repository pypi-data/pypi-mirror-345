# Activate the virtual environment
if (Test-Path ".venv") {
    Write-Host "Activating virtual environment..."
    .\.venv\Scripts\Activate.ps1
} elseif (Test-Path "venv") {
    Write-Host "Activating virtual environment..."
    .\venv\Scripts\Activate.ps1
} elseif (Test-Path "env") {
    Write-Host "Activating virtual environment..."
    .\env\Scripts\Activate.ps1
} elseif (Test-Path ".env") {
    Write-Host "Activating virtual environment..."
    .\.env\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found. Creating one..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
}

# Install the package in development mode
Write-Host "Installing package in development mode..."
pip install -e .

# Run the tests
Write-Host "Running tests..."
python -m unittest discover tests
