import requests
import google.generativeai as genai
from fastapi import FastAPI


# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCeR2fM82VngUKNK-45Cu4xS2ntqhvN9OM"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# OSRM API URL
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"

# Route Calculation Endpoint
def get_fastest_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    url = f"{OSRM_URL}{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"
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
        "steps": data["routes"][0]["legs"][0]["steps"]
    }
    
    
    print(route_info)
    return route_info

# AI-Based Route Optimization (Using Gemini API)
def optimize_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    route_data = get_fastest_route(start_lon, start_lat, end_lon, end_lat)
    
    if "error" in route_data:
        return route_data
    
    prompt = f"""
    Here is a route with coordinates {route_data}.
    Analyze live traffic and suggest a faster route if possible.
    Consider alternative paths and provide an optimized route.
    """
    
    response = model.generate_content(prompt)
    print(response.text)
    return {"optimized_route": response.text}

# Health Check
def health_check():
    return {"status": "RescueRoute AI is running"}

def __main__():
    user_input = input("1: get_fastest_route , 2: optimize_route , 3: health_check ")
    user_input = int(user_input)

    if user_input == 1:
        print(get_fastest_route(-122.42, 37.77,-122.37, 37.78))
    elif user_input == 2:
        optimize_route(-122.42, 37.77,-122.37, 37.78)
    elif user_input == 3:
        health_check()

__main__()