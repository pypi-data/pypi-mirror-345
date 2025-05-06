import requests
import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json



load_dotenv()

class LLM:
    def __init__(self, openai_api_key=None, perplexity_api_key=None, claude_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.perplexity_api_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
        self.claude_api_key = claude_api_key or os.getenv("CLAUDE_API_KEY")
        self.system_prompt = """
                You are a highly experienced SQL expert and database performance optimizer. Your role is to convert user queries written in natural language into the most accurate, syntactically correct, and **optimized SQL queries**.  
                You will be provided with the **database schema** and a **natural language query**.  

                Follow these strict instructions:

                1. **Understand the Schema**: Carefully analyze the table structures, data types, relationships, and any relevant constraints in the schema.
                2. **Interpret the Query**: Extract the user's intent clearly and map it precisely to the schema.
                3. **Generate Optimized SQL**:
                   - Write clean, standard SQL (use the appropriate dialect if specified, such as PostgreSQL, MySQL, etc.).
                   - Prefer **efficient joins**, **indexes**, and **filters** that reduce the data scanned.
                   - Avoid unnecessary subqueries or complex expressions unless essential for accuracy.
                4. **Be Accurate and Safe**:
                   - Do not make assumptions beyond the provided schema.
                   - Avoid SELECT * unless explicitly requested or beneficial.
                   - Ensure aliases are meaningful and improve readability.

                Output format:
                ```json{{
                
                    "sql": "<your SQL query here>",
                    "explaination": "<optional explanation here>"
                    }}```
                
                Respond only with the optimized SQL query.
        """

    def call_perplexity_ai(self, question, model=None, max_tokens=2500, streaming=False):
        # Define the API endpoint and your API key
        api_url = 'https://api.perplexity.ai/chat/completions'
        api_key = self.perplexity_api_key

        if model is None:
            model = 'sonar'
        messages = self.construct_system_prompt(question)
        payload = {
            "model": model,  
            "messages": messages,
            "max_tokens": max_tokens,  
            "temperature": 0.5,
            "return_related_questions": True,
            "stream": streaming,  
            "web_search_options": {"search_context_size": "medium"}
        }

        # Set up the headers for the request
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Make the POST request to the API with streaming enabled
        with requests.post(api_url, headers=headers, data=json.dumps(payload), stream=True, timeout=180) as response:
            if response.status_code == 200:
                # Stream the response content
                if streaming:
                    for line in response.iter_lines():
                        if line:  # Filter out empty lines
                            decoded_line = line.decode('utf-8').strip()
                            decoded_line = decoded_line.replace("data: ", "").strip()
                            for _line in decoded_line.split("\n"):
                                yield json.loads(_line)
                else:
                    # If not streaming, return the entire response
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        yield None
            else:
                print(f"Error: {response.status_code}, {response.text}")

        yield None


    def call_claude_ai(self, questtion, max_tokens=800, model='claude-3-5-sonnet-latest', streaming=False):
        if model is None:
            model = 'claude-3-5-sonnet-latest'
        # print(messages)
        claude_client = Anthropic(
            api_key=self.claude_api_key,
        )
        messages=self.construct_system_prompt(questtion)
        system_prompt = messages[0]['content']
        user_messages = messages[1:]
        stream = claude_client.messages.create(
            max_tokens=max_tokens,
            messages=user_messages,
            system=system_prompt,
            model=model,
            stream=streaming,
        )
        # print(json.dumps(system_prompt, indent=4))
        if streaming:
            return stream

        return stream.choices[0].message.content


    def create_message_dict_o1(self, system_prompt, question, chat_history=None):
        if chat_history is None:
            chat_history = []

        # Start with the system_prompt as the first user message
        messages = [
            {
                "role": "user",  # First message is always user
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ]
            }
        ]

        # Add chat history in alternating user-assistant pairs
        for chat in chat_history:
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": chat[0]
                    }
                ]
            }
            assistant_message = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": chat[1]
                    }
                ]
            }
            messages.append(user_message)
            messages.append(assistant_message)

        # Add the new question as the last user message
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
                }
            ]
        })

        return messages


    def call_openai_o1(self, question, model="o1-preview", max_tokens=800, streaming=False):
        from openai import OpenAI
        client = OpenAI(self.openai_api_key)
        system_prompt = self.construct_system_prompt(question)
        messages = self.create_message_dict_o1(system_prompt, question)
        o1_response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=streaming
        )
        if streaming:
            return o1_response
        return json.loads(o1_response.choices[0].message.content)

    def construct_system_prompt(self, question, system_prompt=None):
        if system_prompt is None:
            system_prompt = self.system_prompt

        messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]

        return messages

    def call_open_ai(self, question, max_tokens=800, model='gpt-4o-mini', streaming=False, response_format=True):
        from openai import OpenAI
        client = OpenAI(api_key=self.openai_api_key)
        system_prompt = self.construct_system_prompt(question)
        # print(json.dumps(system_prompt, indent=4))
        if model is None:
            model = 'gpt-4o-mini'

        # Basic kwargs that work for all models
        kwargs = {
            "model": model,
            "messages": system_prompt,
            "max_completion_tokens": max_tokens,
            "stream": streaming
        }

        # Add response_format for JSON responses
        if response_format:
            kwargs["response_format"] = {"type": "json_object"}

        # Add web search options if model is gpt-4o-search-preview
        if model == 'gpt-4o-search-preview':
            kwargs["web_search_options"] = {"search_context_size": "medium"}

        # Create the completion
        stream = client.chat.completions.create(**kwargs)
        # print(stream)
        if streaming:
            return stream
        # print(stream.choices[0].message.content)
        return json.loads(stream.choices[0].message.content)
    
    def get_system_prompt(self):
        return self.system_prompt
    
    def update_system_prompt(self, new_prompt):
        self.system_prompt = new_prompt
