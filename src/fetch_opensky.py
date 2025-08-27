import requests
import logging

API_URL = "https://opensky-network.org/api/states/all"
PARAMS = {
    "lamin": 16.0,
    "lomin": -34.0,
    "lamax": 47.0,
    "lomax": 46.0
}

logger = logging.getLogger(__name__)

def fetch_opensky_data():
    """Récupère les données depuis l’API OpenSky."""
    try:
        response = requests.get(API_URL, params=PARAMS, timeout=10)
        if response.status_code == 200:
            return response.json().get("states", [])
        else:
            logger.warning(f"OpenSky API returned status {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching OpenSky data: {e}")
        return []
