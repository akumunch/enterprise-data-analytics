import os 
import re 
import psycopg
from langchain_core.tools import tool

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER",
    "TRUNCATE", "CREATE", "GRANT", "REVOKE",
]

def _get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def validate_select_only(sql_query: str) -> str | None:
    """Returns an error message if the query is unsafe, or None if it's fine."""
    stripped = sql_query.strip().rstrip(";")
    if not stripped.upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", stripped, re.IGNORECASE):
            return f"Error: '{keyword}' is not permitted in queries."
    return None

@tool
def query_database(sql_query: str) -> str:
    """
    Run a read-only SQL query against the Northwind database and return the results.
    Only SELECT statements are allowed. Available tables: categories, customer_customer_demo,
    customer_demographics, customers, employee_territories, employees, order_details, orders,
    products, region, shippers, suppliers, territories, us_states.
    """
    # Validate query safety using the shared validation function
    error = validate_select_only(sql_query)
    if error:
        return error
    
    stripped = sql_query.strip().rstrip(";")
    
    try:
        with _get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(stripped)
                    columns = [desc[0] for desc in cur.description]
                    rows = cur.fetchmany(50) #to prevent huge responses - enough for context

                if not rows:
                    return "Query returned no results."

                result_lines = [", ".join(columns)]
                for row in rows:
                    result_lines.append(", ".join(str(v) for v in row))

                return "\n".join(result_lines)
    except psycopg.errors.InsufficientPrivilege:
        return "Error: Insufficient privileges to run this query."
    except Exception as e:
        return f"Database error: {e}"