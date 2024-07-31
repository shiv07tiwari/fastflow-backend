import os
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai

from databases.cache import cache_response
import ollama
from ollama import AsyncClient



class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.json_model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

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

    async def generate_llama_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await AsyncClient().generate(model='llama2', prompt=prompt, stream=stream)
        return response['response']

    async def generate_json_llama_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await AsyncClient().generate(model='llama2', format='json', prompt=prompt, stream=stream)
        return response['response']

