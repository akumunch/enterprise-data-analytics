from langchain_core.tools import tool

@tool
def get_sales_data() -> str:
    """Get the company's sales data."""
    return """
    January: $12000
    February: $15000
    March: $11000
    April: $18000
    May: $21000
    """

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception:
        return "Unable to calculate the expression."