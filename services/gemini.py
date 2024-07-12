import os
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.executor = ThreadPoolExecutor(max_workers=10)  # Adjust the number of workers as needed

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

