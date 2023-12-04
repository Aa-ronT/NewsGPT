import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import time
from exceptions import GoogleApiError

# A class for performing Google searches using the Custom Search JSON API
class GoogleSearcher:
    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx

    async def search_google(self, session, query: str):
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={self.api_key}&cx={self.cx}"
        return await self.fetch(session, search_url)

    async def fetch(self, session, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise GoogleApiError(f"Failed to fetch data, HTTP status: {response.status}")
        except asyncio.TimeoutError:
            raise GoogleApiError("Request to Google API timed out.")
        except aiohttp.ClientError as e:
            raise GoogleApiError(f"Client error: {str(e)}")
        except Exception as e:
            raise GoogleApiError(f"Unexpected error: {str(e)}")
    
    async def perform_search(self, query: str):
        async with aiohttp.ClientSession() as session:
            result = await self.search_google(session, query)
            return [item['link'] for item in result['items']]
        