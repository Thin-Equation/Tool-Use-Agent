from .weather_tool import get_weather_forecast
from .search_tool import search_database
from .utility_tools import get_current_datetime, calculate_expression

# List of all available tools
default_tools = [
    get_weather_forecast,
    search_database,
    get_current_datetime,
    calculate_expression
]
