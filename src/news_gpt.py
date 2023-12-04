from openai_request_handler import Gpt4, ChatGpt
from data_fetcher import GoogleSearcher
from web_scraper import extract_text_from_websites
import os
import asyncio
from dotenv import load_dotenv
from exceptions import GoogleApiError, OpenAiApiError

load_dotenv()

class NewsGPT:

    MAX_CHARS = 50000

    def __init__(self,
        openai_api_key: str = os.getenv('OPENAI_API_KEY'),
        google_custom_search_api: str = os.getenv('GOOGLE_CUSTOM_SEARCH_API'),
        cx: str = os.getenv('CX')
    ):
        # Initialize ChatGPT, GPT-4, and GoogleSearcher with respective API keys and settings
        self.chat_gpt = ChatGpt(openai_api_key)
        self.gpt_4 = Gpt4(openai_api_key)
        self.google_searcher = GoogleSearcher(google_custom_search_api, cx)

    async def get_response(self, prompt: str):
        # Generate a search query and perform a Google search
        google_search_query = await self.generate_search_query(prompt)
        urls = await self.google_searcher.perform_search(google_search_query)
        # Extract text from the fetched URLs and summarize it
        context = await extract_text_from_websites(urls)
        summary = await self.summarize_text(context, prompt)
        # Truncate the summary to a predefined maximum character length
        summary = summary[:self.MAX_CHARS]
        # Get a response based on the prompt and the summarized search data
        answer = await self.get_response_with_search_data(prompt, summary)
        return answer

    async def get_response_with_search_data(self, prompt, search_data):
        # Define the settings for the ChatGPT model including the search data
        model_settings = {
            'model': 'gpt-3.5-turbo-16k',
            'messages': [
                {'role': 'system', 'content': f'Please use the following realtime data from the internet to aid in the answering of the prompt. Please do not remind the user that you do not have internet access. They already know. \n DATA TO HELP AID RESPONSE:  {search_data}'}
            ],
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'max_tokens': 1000,
            'n': 1,
            'temperature': 1,           
            'top_p': 1
        } 
        # Get a response from the ChatGPT model
        response = await self.chat_gpt.get_response(prompt, model_settings=model_settings)
        return response

    async def generate_search_query(self, prompt: str) -> str:
        # Get a response from ChatGPT to generate a search query
        response = await self.chat_gpt.get_response(prompt, model_settings = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': "The input that you will receive is an unformatted prompt. I would like you to rewrite the prompt that is sent. You will rewrite the prompt as one singular google search query that is optimized to provide resources that are most likely to answer the users question in the prompt."}
            ],
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'max_tokens': 1000,
            'n': 1,
            'temperature': 1,
            'top_p': 1,
        })
        # Clean and return the generated search query
        response_string = response['choices'][0]['message']['content']
        response_string = response_string.replace('"', '')
        return response_string  

    async def summarize_text(self, text: str, original_prompt: str) -> str:
        iter_amount = 3000
        summaries = ''
        # Helper function to get model settings
        def get_model_settings():
            model_settings = {
                'model': 'gpt-3.5-turbo',
                'messages': [       
                    {'role': 'system', 'content': f'''Please generate a concise summary of the following text. Focus on capturing the key points, main ideas, and essential details that relate to the original question. The summary should be comprehensive yet brief, offering a clear overview of the text's content. Original question: "{original_prompt}"'''}
                ],
                'frequency_penalty': 0,
                'presence_penalty': 0,
                'max_tokens': 1000,
                'n': 1,
                'temperature': 1,
                'top_p': 1, 
            } 
            return model_settings
        
        tasks = []

        # Divide text into chunks and create tasks for summarizing each chunk
        for i in range(0, len(text), iter_amount):
            task = asyncio.create_task(self.chat_gpt.get_response(text[i:i+iter_amount], model_settings=get_model_settings()))
            tasks.append(task)
            await asyncio.sleep(0.2)
        
        # Collect and concatenate summaries from each chunk
        summary_responses = await asyncio.gather(*tasks, return_exceptions=True)
        for summary_response in summary_responses:
            if 'choices' in summary_response:
                summaries += summary_response['choices'][0]['message']['content']
        
        return summaries    
