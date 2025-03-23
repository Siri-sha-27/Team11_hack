import os
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import requests
import json
from fastapi.responses import HTMLResponse
from typing import List
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific ones in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# OSRM URL for routing
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"

# WebSocket connections
active_connections: List[WebSocket] = []


# Function to get route from OSRM
def get_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    # Construct the OSRM API request URL
    url = f"{OSRM_URL}{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"

    response = requests.get(url)
    data = response.json()

    # Return the route geometry (GeoJSON) and steps data
    print(
        data["routes"][0]["geometry"]["coordinates"],
        data["routes"][0]["legs"][0]["steps"],
    )

    return (
        data["routes"][0]["geometry"]["coordinates"],
        data["routes"][0]["legs"][0]["steps"],
    )


@app.get("/")
async def get():
    # Serve the front-end HTML file for the React app
    return HTMLResponse(open("index.html").read())


@app.websocket("/ws/route")
async def websocket_route(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Wait for the start message containing coordinates from the user
            data = await websocket.receive_json()
            start_lon = data["start_lon"]
            start_lat = data["start_lat"]
            end_lon = data["end_lon"]
            end_lat = data["end_lat"]

            # Get route and steps from OSRM
            route, steps = get_route(start_lon, start_lat, end_lon, end_lat)

            # Send route to React frontend for display
            await websocket.send_json({"route": route, "steps": steps})

    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.websocket("/ws/drive")
async def websocket_drive(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Wait for the start message containing coordinates from the user

            data = await websocket.receive_json()
            start_lon = data["start_lon"]
            start_lat = data["start_lat"]
            end_lon = data["end_lon"]
            end_lat = data["end_lat"]

            route, steps = get_route(start_lon, start_lat, end_lon, end_lat)

            # Start the vehicle simulation
            for step in steps:
                # Simulate movement along the route with speed limits and intervals
                for i in range(0, len(route), 5):  # Move in intervals
                    await websocket.send_json({"position": route[i]})
                    time.sleep(1)  # Simulate one second per update

            await websocket.send_json({"completed": True})

    except WebSocketDisconnect:
        active_connections.remove(websocket)
