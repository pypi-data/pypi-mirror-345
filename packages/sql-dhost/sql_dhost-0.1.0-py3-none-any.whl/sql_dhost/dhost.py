from util import GetDB, LLM

class PSQLUtil:
    def __init__(self, db_connection ,openai_api_key=None, perplexity_api_key=None, claude_api_key=None):
        self.db=GetDB(con_string=db_connection).get_db_connection()
        self.LLM_util = LLM(openai_api_key=openai_api_key, perplexity_api_key=perplexity_api_key, claude_api_key=claude_api_key)
        self.schema = None

    def set_schema(self, schema): 
        self.schema = schema
        system_prompt = f""" {self.LLM_util.get_system_prompt()}\n\n
        The following is the schema of the database:\n{self.schema}\n\n
        You are a SQL expert. You will be given a question and you need to generate a SQL query to answer the question.
        """
        self.LLM_util.update_system_prompt(new_prompt=system_prompt)
        return system_prompt

    def execute_query(self, query, params=None):
        conn = self.db.getconn()

        # Create a cursor object
        cur = conn.cursor()

        if params is None:
            cur.execute(query)
        else:
            # If there are parameters, execute the query with parameters
            cur.execute(query, params)
        # Fetch all results
        results = cur.fetchall()
        # Close the cursor and connection
        cur.close()
        self.db.putconn(conn)
        return results
    
    def update_system_prompt(self, new_prompt):
        self.LLM_util.update_system_prompt(new_prompt=new_prompt)
    
    def get_system_prompt(self):
        return self.LLM_util.get_system_prompt()
    
    def generate_sql_query(self, question, provider="openai", llm=None, max_tokens=1000):
        if self.schema is None:
            raise ValueError("Schema is not set. Please set the schema before generating SQL queries.")
        question = f"Generate a SQL query for the following question: {question} with schema: {self.schema}"

        if provider == "openai":
            response = self.LLM_util.call_open_ai(question=question, model=llm, max_tokens=max_tokens)
        elif provider == "claude":
            response = self.LLM_util.call_claude_ai(question=question, model=llm, max_tokens=max_tokens)
        elif provider == "perplexity":
            response = self.LLM_util.call_perplexity_ai(question=question, model=llm, max_tokens=max_tokens)
        else:
            raise ValueError("Invalid provider. Choose from 'openai', 'claude', or 'perplexity'.")
        if response['sql_query'] is None:
            raise ValueError("SQL query generation failed. Please check the input question.")
        return response
    
    def generate_sql_query_and_execute(self, question, provider="openai", llm=None, max_tokens=800):
        if self.schema is None:
            raise ValueError("Schema is not set. Please set the schema before generating SQL queries.")
        question = f"Generate a SQL query for the following question: {question} with schema: {self.schema}"
        # print(question)
        if provider == "openai":
            response = self.LLM_util.call_open_ai(question=question, model=llm, max_tokens=max_tokens)
            # print(response)
        elif provider == "claude":
            response = self.LLM_util.call_claude_ai(questtion=question, model=llm, max_tokens=max_tokens)
        elif provider == "perplexity":
            response = self.LLM_util.call_perplexity_ai(question=question, model=llm, max_tokens=max_tokens)
        else:
            raise ValueError("Invalid provider. Choose from 'openai', 'claude', or 'perplexity'.")
        if response['sql'] is None:
            raise ValueError("SQL query generation failed. Please check the input question.")
       

        yield f"executing sql query : {response['sql']}"
        yield f"explaination : {response['explaination']}"

        results = self.execute_query(query=response['sql'])
        if len(results) == 0:
            yield "No results found."
        else:
            yield f"Results: {results}"


    
