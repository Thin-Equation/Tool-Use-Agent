from langchain.tools import tool

@tool
def search_database(query: str) -> str:
    """Search a database for information.
    
    Args:
        query: The search query string
    
    Returns:
        Search results from the database.
    """
    # In a real implementation, you would query a database
    # For demonstration purposes, we return a mock response
    mock_results = {
        "weather": "Found 15 records about weather patterns and forecasts.",
        "sales": "Found 34 records about sales data for Q1 2025.",
        "products": "Found 27 records about product inventory and details.",
        "default": f"Found 3 records matching '{query}'."
    }
    
    for key in mock_results:
        if key in query.lower():
            return mock_results[key]
            
    return mock_results["default"]
