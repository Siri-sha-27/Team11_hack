import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAPQUEST_API_KEY = os.getenv("MAPQUEST_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# OSRM API URL
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"


# Route Calculation Endpoint
def get_fastest_route(
    start_lon: float, start_lat: float, end_lon: float, end_lat: float
):
    url = f"{OSRM_URL}{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true&alternatives=3"
    response = requests.get(url)

    if response.status_code != 200:
        print(1)
        return {"error": "Unable to fetch route from OSRM API."}

    data = response.json()
    if "routes" not in data or not data["routes"]:
        print(2)
        return {"error": "No routes found."}

    route_info = {
        "coordinates": data["routes"][0]["geometry"]["coordinates"],
        "steps": data["routes"][0]["legs"][0]["steps"],
    }

    print(route_info)
    return route_info


# AI-Based Route Optimization (Using Gemini API)
def optimize_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    route_data = get_fastest_route(start_lon, start_lat, end_lon, end_lat)

    if "error" in route_data:
        return route_data

    prompt = f"""
    Here are three separate routes encoded in JSON with latitude/longitude, distance, speed, etc. {route_data}.
    I want you to estimate traffic patterns for each route at the current time, and then find the quickest
    route based on the traffic patterns. Please provide the optimized route in JSON format, matching the input
    of the quickest route provided, for my application.
    """

    response = model.generate_content(prompt)
    print(response.text)
    return {"optimized_route": response.text}


# Health Check
def health_check():
    return {"status": "RescueRoute AI is running"}


def traffic_check():
    url = f"https://www.mapquestapi.com/traffic/v2/incidents?key={MAPQUEST_API_KEY}&boundingBox=39.95,-105.25,39.52,-104.71&filters=construction,incidents, event, congestion"
    # https://www.mapquestapi.com/traffic/v2/incidents?key=KEY&boundingBox=39.95,-105.25,39.52,-104.71&filters=construction,incidents
    response = requests.get(url)
    print(response.json())
    return response.json()


def route_analysis(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    # mapquest_url = f"https://www.mapquestapi.com/directions/v2/route?key={MAPQUEST_API_KEY}&from={start_lat},{start_lon}&to={end_lat},{end_lon}"
    mapquest_url = f"https://www.mapquestapi.com/traffic/v2/incidents?key={MAPQUEST_API_KEY}&boundingBox={start_lat},{start_lon},{end_lat},{end_lon}&filters=construction,incidents, event, congestion"
    osm_url = f"https://openstreetmap.org/api/0.6/map?bbox={start_lon},{start_lat},{end_lon},{end_lat}"

    mapquest_response = requests.get(mapquest_url)
    mapquest_json = mapquest_response.json()
    print(mapquest_json)

    route_data = get_fastest_route(start_lon, start_lat, end_lon, end_lat)

    prompt = f"""
    Attached are both traffic data and node/vertice information for a street network displayed using 
    latitude-longitude values in a bounding box {route_data} {mapquest_json}. I want you to observe the traffic patterns and return the quickest route based on the traffic patterns. Please only provide the response in JSON format, matching the input of the quickest route provided, for I am using this as an API. DO NOT provide any other information.
    Example JSON format:

      "coordinates": [ [], [] ... ] , "steps": [ [], [] ... ]
      """

    response = model.generate_content(prompt)
    print(response.text)
    return response.text


def speed_analysis(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    mapquest_url = f"https://www.mapquestapi.com/traffic/v2/incidents?key={MAPQUEST_API_KEY}&boundingBox={start_lat},{start_lon},{end_lat},{end_lon}&filters=construction,incidents, event, congestion"
    # osm_url = f"https://openstreetmap.org/api/0.6/map?bbox={start_lon},{start_lat},{end_lon},{end_lat}"

    mapquest_response = requests.get(mapquest_url)
    mapquest_json = mapquest_response.json()
    # print(mapquest_json)

    route_data = get_fastest_route(start_lon, start_lat, end_lon, end_lat)

    prompt = f"""
    Attached are both traffic data and node/vertice information for a street network displayed using
    latitude-longitude values in a bounding box {route_data} {mapquest_json}. I want you to observe the traffic patterns and provide a time estimate for this trip (seconds), and return an integer value. 

    response: Integer
      """

    response = model.generate_content(prompt)
    raw_response = response.text
    print(raw_response)
    return raw_response


def __main__():
    user_input = input("1: get_fastest_route , 2: optimize_route , 3: health_check ")
    user_input = int(user_input)

    if user_input == 1:
        print(get_fastest_route(-122.42, 37.77, -122.37, 37.78))
    elif user_input == 2:
        optimize_route(-122.42, 37.77, -122.37, 37.78)
    elif user_input == 3:
        health_check()
    elif user_input == 4:
        traffic_check()
    elif user_input == 5:
        route_analysis(-122.42, 37.77, -122.37, 37.78)
    elif user_input == 6:
        print(speed_analysis(-122.42, 37.77, -122.37, 37.78))


__main__()
