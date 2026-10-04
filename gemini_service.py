import json
import os

import streamlit as st
from google import genai
from google.genai import types


def get_api_key():

    try:

        key = st.secrets.get(
            "GEMINI_API_KEY",
            ""
        )

        if key:
            return key

    except Exception:
        pass

    return os.getenv(
        "GEMINI_API_KEY",
        ""
    )


class GeminiService:

    def __init__(self):

        api_key = get_api_key()

        if not api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to Streamlit Secrets or your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

    def generate(
        self,
        prompt,
        use_search=False,
    ):

        config = None

        if use_search:

            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        return response.text

    def generate_json(
        self,
        prompt,
        use_search=False,
    ):

        search_instruction = ""

        if use_search:

            search_instruction = """
Use Google Search to research current information.

Prioritize:
1. Official government websites
2. Official university websites
3. Official organization websites
4. Reliable secondary sources

Do not invent URLs or requirements.
"""

        full_prompt = f"""
You are an expert AI case manager.

{search_instruction}

Return ONLY valid JSON.

{prompt}
"""

        config_args = {
            "response_mime_type": "application/json"
        }

        if use_search:

            config_args["tools"] = [
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]

        config = types.GenerateContentConfig(
            **config_args
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=config,
        )

        text = response.text.strip()

        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        return json.loads(text)
