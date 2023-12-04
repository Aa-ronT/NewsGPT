import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from exceptions import HttpsError
import chardet

# Set a timeout for all HTTP requests
timeout = aiohttp.ClientTimeout(total=3)

async def extract_text_from_website(url: str, session) -> str:
    try:
        # Make an asynchronous GET request to the URL
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                # Read raw response and detect encoding
                raw = await response.read()
                encoding = chardet.detect(raw)['encoding']
                # Decode response using detected encoding
                text = raw.decode(encoding)
                # Parse the HTML and extract text
                soup = BeautifulSoup(text, 'lxml')
                page_text = soup.get_text()
                page_text.strip()
                return page_text
            else:
                return ''
    except Exception as error:
        print(error)
        return ''

async def extract_text_from_websites(urls: list):
    websites_text = ''

    # Create a ClientSession for making HTTP requests
    async with aiohttp.ClientSession() as session:
        # Extract text from each website concurrently
        results = await asyncio.gather(*(extract_text_from_website(url, session) for url in urls))

        # Concatenate text from all websites
        for result in results:
             if result:
                websites_text += result

    # Raise an error if no text was extracted
    if not websites_text:
        raise HttpsError('Failed to extract text from the provided URLs.')

    return websites_text