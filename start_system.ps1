Write-Host "Starting Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" -WorkingDirectory $PSScriptRoot

Write-Host "Starting Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WorkingDirectory $PSScriptRoot

Write-Host "System Started. Access frontend at http://localhost:5173"
