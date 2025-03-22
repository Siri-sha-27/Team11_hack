#!/bin/bash

# Navigate to server directory and start FastAPI server
cd server
uvicorn server:app --reload &

# Navigate to client directory and start Vite React app
cd ../client
npm run dev
