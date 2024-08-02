import google.generativeai as genai

from ollama import AsyncClient

from databases.cache import fetch_cached_response_for_hex_code
from services.utils import string_to_hex


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.json_model = genai.GenerativeModel('gemini-1.5-flash',
                                                generation_config={"response_mime_type": "application/json"})

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_json_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.json_model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_cached_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        hex_code = string_to_hex(prompt)
        cached_response = await fetch_cached_response_for_hex_code(hex_code)
        if cached_response:
            return cached_response
        print("LLM Cache miss : ", hex_code)
        response = await self.json_model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_llama_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await AsyncClient().generate(model='llama2', prompt=prompt, stream=stream)
        return response['response']

    async def generate_json_llama_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await AsyncClient().generate(model='llama2', format='json', prompt=prompt, stream=stream)
        return response['response']
