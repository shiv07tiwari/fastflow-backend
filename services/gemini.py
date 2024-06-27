import os
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai


class GeminiService:
    def __init__(self):
        API_KEY = os.getenv("GEMINI_API_KEY", None)
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.executor = ThreadPoolExecutor(max_workers=10)  # Adjust the number of workers as needed

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response

