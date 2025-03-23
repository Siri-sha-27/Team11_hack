from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from collections import deque
import json
import requests
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAPQUEST_API_KEY = os.getenv("MAPQUEST_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def get_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    url = f"{OSRM_URL}{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"

    response = requests.get(url)
    data = response.json()

    # Return route geometry (GeoJSON format)
    route = data["routes"][0]["geometry"]["coordinates"]
    steps = data["routes"][0]["legs"][0]["steps"]
    return route, steps


def speed_analysis(
    route_data, start_lon: float, start_lat: float, end_lon: float, end_lat: float
):
    mapquest_url = f"https://www.mapquestapi.com/traffic/v2/incidents?key={MAPQUEST_API_KEY}&boundingBox={start_lat},{start_lon},{end_lat},{end_lon}&filters=construction,incidents, event, congestion"
    # osm_url = f"https://openstreetmap.org/api/0.6/map?bbox={start_lon},{start_lat},{end_lon},{end_lat}"

    mapquest_response = requests.get(mapquest_url)
    mapquest_json = mapquest_response.json()
    print(mapquest_json)

    prompt = f"""
    Attached are both traffic data and node/vertice information for a street network displayed using
    latitude-longitude values in a bounding box {route_data} {mapquest_json}. I want you to observe the traffic patterns and provide a list of integer values as an estimate of speed in mph.

      "speed": [ ... ]
      """

    response = model.generate_content(prompt)
    raw_response = response.text
    print(raw_response)
    try:
        cleaned_json = raw_response.replace("```json", "").replace("```", "").strip()

        data = json.loads(cleaned_json)
        return data

    except Exception as e:
        print(f"JSON parsing error: {e}")
        return route_data


# print(response.text)
# return response.text


app = FastAPI()

help_request_queue = deque()

responders = set()
users = set()


@app.websocket("/ws/request")
async def request_help(websocket: WebSocket):
    await websocket.accept()
    users.add(websocket)

    print("New user connected")
    try:
        while True:
            data = await websocket.receive_text()
            print(data, "REQUEST")
            request_data = json.loads(data)

            help_request = {
                "timestamp": request_data.get("timestamp"),
                "user_lat": request_data.get("user_lat"),
                "user_lon": request_data.get("user_lon"),
            }

            help_request_queue.append(help_request)
            print(f"New help request added: {help_request}")

            for responder in responders:

                await responder.send_json(
                    json.loads(
                        json.dumps(
                            {
                                "type": "new_request",
                                "requests": list(
                                    help_request_queue
                                ),  # Ensure it is serializable
                            }
                        )
                    )
                )

    except WebSocketDisconnect:
        users.remove(websocket)


@app.websocket("/ws/route")
async def websocket_route(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            start_lon = data["start_lon"]
            start_lat = data["start_lat"]
            end_lon = data["end_lon"]
            end_lat = data["end_lat"]

            route, steps = get_route(start_lon, start_lat, end_lon, end_lat)
            # speed = speed_analysis(route, start_lon, start_lat, end_lon, end_lat)
            # route, steps = route_analysis(start_lon, start_lat, end_lon, end_lat)

            # await websocket.send_json({"route": route})
            await websocket.send_json({"route": route, "steps": steps})

    except WebSocketDisconnect:
        pass


@app.websocket("/ws/respond")
async def respond(websocket: WebSocket):
    await websocket.accept()
    responders.add(websocket)

    try:
        await websocket.send_json(
            {"type": "new_request", "requests": list(help_request_queue)}
        )

        while True:
            data = await websocket.receive_text()

            response_data = json.loads(data)

            if response_data.get("type") == "accept_request":
                if help_request_queue:
                    accepted_request = help_request_queue.popleft()

                    print(f"Request accepted: {accepted_request}")
                    print(f"Remaining requests: {help_request_queue}")
                    print(f"Getting route... {accepted_request}")

                    start_lon = response_data["responder_lon"]
                    start_lat = response_data["responder_lat"]
                    print(
                        f"Responder location: {start_lon}, {start_lat}, User location: {accepted_request['user_lon']}, {accepted_request['user_lat']}"
                    )
                    end_lon = accepted_request["user_lon"]
                    end_lat = accepted_request["user_lat"]

                    route, steps = get_route(start_lon, start_lat, end_lon, end_lat)

                    # route, steps = route_analysis(
                    #     start_lon, start_lat, end_lon, end_lat
                    # )

                    # route = route_analysis(start_lon, start_lat, end_lon, end_lat)

                    for user in users:
                        await user.send_json(
                            # {"type": "route", "route": route}
                            {"type": "route", "route": route, "steps": steps}
                        )

                    await websocket.send_json(
                        # {"type": "route", "route": route}
                        {"type": "route", "route": route, "steps": steps}
                    )

    except WebSocketDisconnect:
        responders.remove(websocket)
