import requests
import re

TOMTOM_API_KEY = "sN9Zz2SMHJLIA8yjVutf26Jik9ZZKxKn" 

def extract_location(query):
    query = query.lower().strip()
    query = re.sub(r"\b(traffic|update|updates|for|in|whats|what's|is|the|now|current|situation)\b", "", query, flags=re.IGNORECASE).strip()
    return query if query else None

def get_coordinates(location):
    url = f"https://api.tomtom.com/search/2/geocode/{location}.json"
    params = {"key": TOMTOM_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            lat = data["results"][0]["position"]["lat"]
            lon = data["results"][0]["position"]["lon"]
            return lat, lon

        return None, None
    except requests.exceptions.RequestException:
        return None,None

def get_traffic_info(query):
    location = extract_location(query)

    if not location:
        return "Please specify a location, e.g., 'Traffic in Kolkata'."
    lat, lon = get_coordinates(location)
    if not lat or not lon:
        return f"Could not determine coordinates for {location}. Try a different city."

    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {"key": TOMTOM_API_KEY, "point": f"{lat},{lon}"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "flowSegmentData" in data:
            current_speed = data["flowSegmentData"]["currentSpeed"]
            free_flow_speed = data["flowSegmentData"]["freeFlowSpeed"]
            congestion_level = "High" if current_speed < (free_flow_speed * 0.6) else "Moderate"

            return f"Traffic update for {location}: Current speed is {current_speed} km/h. Congestion level: {congestion_level}."
        
        return f"No real-time traffic updates available for {location}."

    except requests.exceptions.RequestException as e:
        return f"Error fetching traffic information: {e}"
    
import requests