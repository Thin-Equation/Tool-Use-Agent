from langchain.tools import tool
import requests

@tool
def get_weather_forecast(location: str) -> str:
    """Get the weather forecast for a specific location.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
        date: The date to get the forecast for, e.g. 2025-03-19
    
    Returns:
        The weather forecast for the specified location.
    """
    # In a real implementation, you would call a weather API
    # For demonstration purposes, we return a mock response
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": os.getenv("WEATHER_API_KEY"),
        "q": location,
        "aqi": "no"
    }
    response = requests.get(url, params=params)
    return {
        "temperature": response.json()['current']['temp_c'],
        "condition": response.json()['current']['condition']['text'],
        "humidity": response.json()['current']['humidity']
    }
