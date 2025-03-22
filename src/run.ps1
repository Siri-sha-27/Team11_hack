# run.ps1

# Start FastAPI server (Python)
Start-Process "python" -ArgumentList "-m uvicorn server.main:app --reload"

# Start Vite React app
Start-Process "npm" -ArgumentList "run dev --prefix client"
