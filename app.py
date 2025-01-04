import logging
from time import time
from flask import Flask, render_template, request
import requests
import json


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

API_KEYS = {
    "tomtom": "AZs9AKSulWIFrsleNNdxVZLgLFDkzRys",
    "aqicn": "7b57197f425ee987e5af6668a23aebfb21b92364",
    "geocoding": "f1b9888311f34061abccbc8754113aaa"
}

BASE_URLS = {
    "tomtom": "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json",
    "aqicn": "https://api.waqi.info/feed",
    "geocoding": "https://api.opencagedata.com/geocode/v1/json",
    "osrm": "http://router.project-osrm.org/route/v1/driving"
}

cache = {}

def log_response_time(api_name, start_time, end_time):
    response_time = end_time - start_time
    logging.info(f"{api_name} API response time: {response_time:.2f} seconds")

def make_request(url, params, api_name):
    try:
        start_time = time()
        response = requests.get(url, params=params)
        end_time = time()
        log_response_time(api_name, start_time, end_time)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in {api_name} API: {e}")
        return {"error": str(e)}

def get_coordinates(location):
    if location in cache:
        return cache[location]
    
    url = BASE_URLS["geocoding"]
    params = {"q": location, "key": API_KEYS["geocoding"]}
    data = make_request(url, params, "Geocoding")
    if "results" in data and data["results"]:
        coordinates = data["results"][0]["geometry"]
        cache[location] = (coordinates["lat"], coordinates["lng"])
        return coordinates["lat"], coordinates["lng"]
    return None, None

def fetch_route(start_coords, end_coords):
    url = f"{BASE_URLS['osrm']}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    params = {"overview": "simplified", "geometries": "geojson"}
    data = make_request(url, params, "OSRM")
    if "routes" in data and data["routes"]:
        return [{"distance": route["distance"], "duration": route["duration"]} for route in data["routes"]]
    return None

def fetch_weather_data(city):
    url = f"{BASE_URLS['aqicn']}/{city}/"
    params = {"token": API_KEYS["aqicn"]}
    data = make_request(url, params, "AQICN")
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
        air_quality = data["data"].get("aqi", "N/A")
        temperature = data["data"]["iaqi"].get("t", {}).get("v", "N/A")
        return {"air_quality": air_quality, "temperature": f"{temperature}" if temperature != "N/A" else "N/A"}
    return {"error": "Could not fetch weather data. Please try again."}

def fetch_traffic_data(lat, lon):
    url = BASE_URLS["tomtom"]
    params = {"key": API_KEYS["tomtom"], "point": f"{lat},{lon}"}
    data = make_request(url, params, "TomTom")
    if "flowSegmentData" in data:
        return {
            "current_speed": data["flowSegmentData"].get("currentSpeed", "N/A"),
            "free_flow_speed": data["flowSegmentData"].get("freeFlowSpeed", "N/A")
        }
    return None

def calculate_emissions(distance_km, fuel_efficiency_kmpl):
    return (distance_km / fuel_efficiency_kmpl) * 2392

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_location = request.form["start_location"]
        end_location = request.form["end_location"]
        vehicle_type = request.form["vehicle_type"]
        try:
            fuel_efficiency = float(request.form["fuel_efficiency"])
        except ValueError:
            logging.warning("Invalid fuel efficiency entered.")
            return "Invalid fuel efficiency. Please enter a valid number."
        
        start_coords = get_coordinates(start_location)
        end_coords = get_coordinates(end_location)
        if not start_coords or not end_coords:
            logging.warning("Could not fetch coordinates.")
            return "Could not fetch coordinates. Please try again."

        routes = fetch_route(start_coords, end_coords)
        if not routes:
            logging.warning("Could not fetch route data.")
            return "Could not fetch route data. Please try again."

        distance_km = routes[0]["distance"] / 1000
        
        if distance_km < 1:
            return "The distance is too short. Please consider walking or cycling."

        if distance_km > 1000:
            return "The distance is too large. Long-distance travel might take considerable time."

        weather_data = fetch_weather_data(start_location)
        traffic_data = fetch_traffic_data(*start_coords)

        emissions = calculate_emissions(distance_km, fuel_efficiency)

        return render_template(
            "result.html",
            start_location=start_location,
            end_location=end_location,
            routes=routes,
            vehicle_type=vehicle_type,
            emissions=emissions,
            weather_data=weather_data,
            traffic_data=traffic_data
        )
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True)
