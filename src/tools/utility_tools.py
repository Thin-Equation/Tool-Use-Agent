from langchain.tools import tool
import datetime

@tool
def get_current_datetime() -> str:
    """Get the current date and time.
    
    Returns:
        The current date and time in ISO format.
    """
    return datetime.datetime.now().isoformat()

@tool
def calculate_expression(expression: str) -> str:
    """Calculate the result of a mathematical expression.
    
    Args:
        expression: A mathematical expression as a string (e.g., "2 + 2 * 3")
    
    Returns:
        The result of the calculation.
    """
    try:
        # Warning: eval can be dangerous in production without proper sanitization
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"
