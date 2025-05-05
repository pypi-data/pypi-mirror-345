from sql_dhost.dhost import PSQLUtil 
import os

DB_CONNECTION_STRING = os.getenv("DB_URL")  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")  
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")  

# Sample schema
SCHEMA = """
Tables:
1. users(id INT, name TEXT, age INT, email TEXT)
2. orders(id INT, user_id INT, product TEXT, amount DECIMAL, order_date DATE)
"""



# Sample natural language question
# QUESTION = "What are the names and total spending of users who placed more than 2 orders?"
QUESTION = "Find the most expensive order for each user, including the user name, order ID, and the amount."

# Initialize the utility
psql_util = PSQLUtil(
    db_connection=DB_CONNECTION_STRING,
    openai_api_key=OPENAI_API_KEY,
    perplexity_api_key=PERPLEXITY_API_KEY,
    claude_api_key=CLAUDE_API_KEY
)

# Set schema and system prompt
psql_util.set_schema(SCHEMA)

# Generate and execute the SQL query
try:
    for step in psql_util.generate_sql_query_and_execute(
        question=QUESTION
    ):
        print(step)
except Exception as e:
    print(f"Error: {e}")
