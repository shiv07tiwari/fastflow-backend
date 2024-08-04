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
        self.openai_client = openai.AsyncClient(api_key=os.getenv('OPENAI_API_KEY'))
        self.USE_GEMINI = True

    async def generate_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_json_response(self, prompt, name, stream):
        print("Generating response for: ", name)
        response = await self.json_model.generate_content_async(prompt, stream=stream)
        return response.text

    async def generate_cached_response(self, prompt, name, stream):
        hex_code = string_to_hex(prompt)
        print("Generating response for: ", hex_code, " ", name)
        cached_response = await fetch_cached_response_for_hex_code(hex_code)
        if cached_response:
            return cached_response
        print("LLM Cache miss : ", hex_code)
        if self.USE_GEMINI:
            response = await self.model.generate_content_async(prompt, stream=stream)
            final_response = response.text
        else:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=False,
            )
            final_response = response.choices[0].message.content

        await set_cached_response_for_hex_code(hex_code, final_response)
        return final_response

    async def generate_cached_json_response(self, prompt, name, stream):
        hex_code = string_to_hex(prompt)
        print("Generating response for: ", hex_code, " ", name)
        cached_response = await fetch_cached_response_for_hex_code(hex_code)
        if cached_response:
            return json.loads(cached_response)
        print("LLM Cache miss : ", hex_code)
        if self.USE_GEMINI:
            response = await self.json_model.generate_content_async(prompt, stream=stream)
            final_response = response.text
        else:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=False,
                response_format={"type": "json_object"}
            )
            final_response = response.choices[0].message.content

        await set_cached_response_for_hex_code(hex_code, final_response)
        final_response = json.loads(final_response)
        return final_response
