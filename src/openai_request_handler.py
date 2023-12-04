import aiohttp
import json
import asyncio 
from exceptions import OpenAiApiError

# Set a timeout for all HTTP requests
timeout = aiohttp.ClientTimeout(10)

# Base class for API interactions
class APIBase:
    BASE_URL = 'https://api.openai.com/v1'

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Standard headers for API requests
        self.headers = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key}

# Base class for interacting with specific models
class ModelBase(APIBase):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Settings specific to the model
        self.model_settings = None
        self.model_endpoint = None

    # Method to send a prompt and get a response from the model
    async def get_response(self, prompt, model_settings: dict = None, headers: dict = None):
        # Use default model settings if none are provided
        if model_settings is None:  
            model_settings = self.model_settings
        
        # Use default headers if none are provided
        if headers is None:
            headers = self.headers
        
        # Check for required keys in model settings
        required_keys = ['model', 'max_tokens', 'messages']
        missing_keys = [key for key in required_keys if not model_settings.get(key)]
        if missing_keys:
            raise Exception(f"Must include these default parameters within the model_settings: {', '.join(missing_keys)}")

        # Append the user's prompt to the messages
        model_settings['messages'].append({'role': 'user', 'content': prompt})

        # Perform the HTTP POST request
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f'{self.BASE_URL}{self.model_endpoint}',
                                        headers=headers, data=json.dumps(model_settings)) as response:
                    if response.status == 200 and response.headers['Content-Type'] == 'application/json':
                        response_data = await response.json()
                        if 'choices' in response_data:
                            return response_data
                        else:
                            raise OpenAiApiError(f"Response from {model_settings['model']} model did not include 'choices'.")
                    else:
                        raise OpenAiApiError(f"The API request to {model_settings['model']} model failed with status {response.status}.")
            except asyncio.TimeoutError:
                raise OpenAiApiError("The request to OpenAI API timed out.")
            except aiohttp.ClientError as e:
                raise OpenAiApiError(f"Failed to fetch response due to client error: {str(e)}")
            except Exception as e:
                raise OpenAiApiError(f"An unexpected error occurred: {str(e)}")

    # Method to update default model settings
    def update_default_settings(self, settings_to_update: dict):
        for key in settings_to_update.keys():
            if key in self.model_settings:
                self.model_settings[key] = settings_to_update[key]
            else:   
                print(f"Warning: Key '{key}' is not a valid setting and will be ignored.")

# Class for interactions with the ChatGPT model
class ChatGpt(ModelBase):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Define the endpoint and initial settings for ChatGPT
        self.model_endpoint = '/chat/completions'
        self.model_settings = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': "You are a helpful assistant."}
            ],
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'max_tokens': 1000,
            'n': 1,
            'temperature': 1,
            'top_p': 1,
        }

# Class for interactions with the GPT-4 model
class Gpt4(ModelBase):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Define the endpoint and initial settings for GPT-4
        self.model_endpoint = '/chat/completions'
        self.model_settings = {
            'model': 'gpt-4',
            'messages': [
                {'role': 'system', 'content': "You are a helpful assistant."}
            ],
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'max_tokens': 1000,
            'n': 1,
            'temperature': 1,
            'top_p': 1,
        }
        