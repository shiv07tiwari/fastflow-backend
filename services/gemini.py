import os
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai

from databases.cache import cache_response


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.json_model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        self.executor = ThreadPoolExecutor(max_workers=10)  # Adjust the number of workers as needed

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_json_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.json_model.generate_content_async(prompt, stream=stream)
        return response.text

    @cache_response()
    async def generate_cached_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

