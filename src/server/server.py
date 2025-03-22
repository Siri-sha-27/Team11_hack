import os
import asyncio
import json
import requests
from fastapi import FastAPI, WebSocket
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

if not MAPBOX_API_KEY:
    raise ValueError("Missing MAPBOX_API_KEY. Please set it in .env file.")

# Mapbox Directions API URL
MAPBOX_URL = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"

app = FastAPI()

# Define Start & End GPS Coordinates
start_coords = [-122.4200, 37.7700]  # Example: San Francisco
end_coords = [-122.4100, 37.7800]


# Get Route from Mapbox
def get_route():
    url = f"{MAPBOX_URL}{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    params = {"access_token": MAPBOX_API_KEY, "geometries": "geojson", "steps": "true"}

    response = requests.get(url, params=params)
    data = response.json()

    # Extracting the route coordinates
    route_coords = data["routes"][0]["geometry"]["coordinates"]
    return [(lat, lon) for lon, lat in route_coords]  # Convert to (lat, lon)


route_coords = get_route()


@app.websocket("/ws/route")
async def route_tracking(websocket: WebSocket):
    await websocket.accept()

    total_distance = sum(
        geodesic(route_coords[i], route_coords[i + 1]).meters
        for i in range(len(route_coords) - 1)
    )
    speed_mps = 10  # Simulate speed of 10m/s
    traveled_distance = 0

    for i in range(len(route_coords) - 1):
        traveled_distance += geodesic(route_coords[i], route_coords[i + 1]).meters
        progress = traveled_distance / total_distance
        current_position = route_coords[i]

        await websocket.send_text(
            json.dumps(
                {
                    "lat": current_position[0],
                    "lon": current_position[1],
                    "progress": progress,
                }
            )
        )
        await asyncio.sleep(1)  # Simulate real-time updates

    await websocket.send_text(
        json.dumps(
            {
                "lat": route_coords[-1][0],
                "lon": route_coords[-1][1],
                "progress": 1.0,
                "completed": True,
            }
        )
    )

    print(
        json.dumps(
            {
                "lat": route_coords[-1][0],
                "lon": route_coords[-1][1],
                "progress": 1.0,
                "completed": True,
            }
        )
    )
