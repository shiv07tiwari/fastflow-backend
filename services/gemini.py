import json
import os

import google.generativeai as genai
import openai

from databases.cache import fetch_cached_response_for_hex_code, set_cached_response_for_hex_code
from services.utils import string_to_hex


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.json_model = genai.GenerativeModel('gemini-1.5-flash',
                                                generation_config={"response_mime_type": "application/json"})
        self.USE_GEMINI = True

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_json_response(self, prompt, name, stream, img):
        print("Generating response for: ", name)
        inputs = [prompt, img] if img else [prompt]
        response = await self.json_model.generate_content_async(inputs, stream=stream)
        return json.loads(response.text)

    async def generate_cached_response(self, prompt, name, stream):
        hex_code = string_to_hex(prompt)
        print("Generating response for: ", hex_code, " ", name)
        cached_response = await fetch_cached_response_for_hex_code(hex_code)
        if cached_response:
            return cached_response
        print("LLM Cache miss : ", hex_code)
        response = await self.model.generate_content_async(prompt, stream=stream)
        final_response = response.text
        await set_cached_response_for_hex_code(hex_code, final_response)
        return final_response

    async def generate_cached_json_response(self, prompt, name, stream, img) -> dict:
        hex_code = string_to_hex(prompt)
        print("Generating response for: ", hex_code, " ", name)
        cached_response = await fetch_cached_response_for_hex_code(hex_code)
        if cached_response:
            return json.loads(cached_response)
        print("LLM Cache miss : ", hex_code)
        inputs = [prompt, img] if img else [prompt]
        response = await self.json_model.generate_content_async(inputs, stream=stream)
        final_response = response.text

        await set_cached_response_for_hex_code(hex_code, final_response)
        final_response = json.loads(final_response)
        return final_response
